"""
Embeds AI-generated news summaries (never raw article text — keeps this
copyright-clean) into a local Chroma vector store using a free local
embedding model (no API cost, no rate limits).
"""
import logging

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

from backend.db.session import get_session, init_db
from backend.models.models import News, NewsAISummary, NewsCompanyTag, Company
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_embedder = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def get_collection():
    client = PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return client.get_or_create_collection("news_summaries")


def build_index() -> int:
    init_db()
    session = get_session()
    embedder = get_embedder()
    collection = get_collection()

    indexed = 0
    try:
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.is_duplicate.is_(False))
            .all()
        )

        existing_ids = set(collection.get()["ids"]) if collection.count() > 0 else set()

        for news, summary in rows:
            doc_id = f"news_{news.news_id}"
            if doc_id in existing_ids:
                continue

            companies = (
                session.query(Company.name)
                .join(NewsCompanyTag, NewsCompanyTag.company_id == Company.company_id)
                .filter(NewsCompanyTag.news_id == news.news_id)
                .all()
            )
            company_names = ", ".join(c[0] for c in companies) or "none"

            text = (
                f"{news.title}\n{summary.ai_summary}\n"
                f"Why it matters: {summary.why_it_matters}"
            )
            embedding = embedder.encode(text).tolist()

            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "url": news.url,
                    "source": news.source,
                    "published_at": str(news.published_at),
                    "classification": summary.classification,
                    "scope": summary.scope,
                    "companies": company_names,
                }],
            )
            indexed += 1

        logger.info("Indexed %d new summaries into Chroma.", indexed)
        return indexed
    finally:
        session.close()


if __name__ == "__main__":
    build_index()
