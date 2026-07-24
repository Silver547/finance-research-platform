"""
Builds a daily/weekly/monthly digest from what's already in the DB
(no new LLM calls needed for the raw data — it just composes what the
tagging/impact agents already produced, plus one LLM call to write the
narrative wrap-up).
"""
import argparse
from datetime import date, timedelta

from backend.db.session import get_session, init_db
from backend.models.models import News, NewsAISummary, Report
from utils.llm_client import call_llm

PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def build_report(period: str = "daily") -> str:
    init_db()
    session = get_session()
    try:
        days = PERIOD_DAYS.get(period, 1)
        cutoff = date.today() - timedelta(days=days)

        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.published_at >= cutoff)
            .filter(News.is_duplicate.is_(False))
            .order_by(News.published_at.desc())
            .all()
        )

        if not rows:
            content = f"No processed news items found for the {period} period."
        else:
            bullet_lines = []
            for news, summary in rows:
                bullet_lines.append(
                    f"- [{summary.classification}/{summary.scope}] {news.title}\n"
                    f"  Why it matters: {summary.why_it_matters}"
                )
            digest_material = "\n".join(bullet_lines)

            prompt = (
                f"You are writing a {period} financial research digest for a student investor. "
                "Using ONLY the bullet points below (already-summarized, already-classified "
                "news items), write a concise narrative overview: what mattered most, any themes "
                "connecting multiple items, and what to watch next. Do not recommend buying or "
                "selling anything.\n\n"
                f"{digest_material}"
            )
            try:
                narrative = call_llm(prompt)
            except Exception as exc:
                narrative = (
                    "AI narrative unavailable today (likely hit the free daily "
                    f"quota). Raw items are still listed below. ({exc})"
                )
            content = f"{narrative}\n\n---\n\n### Raw items covered\n\n{digest_material}"

        report = Report(report_type=period, report_date=date.today(), content=content)
        session.add(report)
        session.commit()
        return content
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], default="daily")
    args = parser.parse_args()
    print(build_report(args.period))
