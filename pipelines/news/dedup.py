"""
Mark duplicate news within a recent lookback window using simple title
similarity (difflib) — free, no embedding cost. For a student-scale project
this catches most re-published wire stories without needing a vector call
for every single headline.
"""
import logging
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from backend.db.session import get_session, init_db
from backend.models.models import News

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.85
LOOKBACK_DAYS = 3


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def mark_duplicates() -> int:
    init_db()
    session = get_session()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
        recent = (
            session.query(News)
            .filter(News.published_at >= cutoff)
            .order_by(News.published_at.asc())
            .all()
        )

        seen: list[News] = []
        dup_count = 0
        for item in recent:
            if item.is_duplicate:
                seen.append(item)
                continue
            is_dup = False
            for prior in seen:
                if _similar(item.title, prior.title) >= SIMILARITY_THRESHOLD:
                    is_dup = True
                    break
            if is_dup:
                item.is_duplicate = True
                dup_count += 1
            seen.append(item)

        session.commit()
        logger.info("Flagged %d duplicate headlines out of %d checked.", dup_count, len(recent))
        return dup_count
    finally:
        session.close()


if __name__ == "__main__":
    mark_duplicates()
