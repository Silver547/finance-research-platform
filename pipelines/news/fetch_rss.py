"""
Fetch headlines from configured free RSS feeds and store new items in the DB.
Idempotent: re-running skips URLs already stored.
"""
import hashlib
import logging
from datetime import datetime, timezone

import feedparser

from backend.db.session import get_session, init_db
from backend.models.models import News
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_published(entry) -> datetime:
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fetch_and_store() -> int:
    init_db()
    session = get_session()
    new_count = 0
    try:
        for source, url in settings.NEWS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                logger.warning("Failed to fetch feed %s: %s", source, exc)
                continue

            for entry in feed.entries:
                link = getattr(entry, "link", None)
                title = getattr(entry, "title", None)
                if not link or not title:
                    continue

                exists = session.query(News).filter_by(url=link).first()
                if exists:
                    continue

                news_item = News(
                    title=title,
                    url=link,
                    source=source,
                    published_at=_parse_published(entry),
                    raw_hash=hashlib.sha256(title.encode("utf-8")).hexdigest(),
                    quality_flag="unverified",
                )
                session.add(news_item)
                new_count += 1

            session.commit()
        logger.info("Ingested %d new headlines.", new_count)
        return new_count
    finally:
        session.close()


if __name__ == "__main__":
    fetch_and_store()
