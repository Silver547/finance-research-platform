"""
One-time seed script: creates Industry rows for every sector in
config.settings.TRACKED_INDUSTRIES so the Sectors page has something to
attach tagged news to immediately. Safe to re-run.

Usage: python scripts_seed_industries.py
"""
from backend.db.session import get_session, init_db
from backend.models.models import Industry
from config.settings import settings


def seed():
    init_db()
    session = get_session()
    try:
        created = 0
        for name in settings.TRACKED_INDUSTRIES:
            if not session.query(Industry).filter_by(name=name).first():
                session.add(Industry(name=name))
                created += 1
        session.commit()
        print(f"Seeded {created} new industries.")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
