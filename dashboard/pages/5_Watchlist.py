import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from backend.db.session import get_session, init_db
from backend.models.models import User, Watchlist, Company
from dashboard.db_helpers import get_all_companies, get_news_for_company

st.set_page_config(page_title="Watchlist", layout="wide")
st.title("⭐ Watchlist")

init_db()
session = get_session()

DEFAULT_USERNAME = "student"
user = session.query(User).filter_by(username=DEFAULT_USERNAME).first()
if not user:
    user = User(username=DEFAULT_USERNAME)
    session.add(user)
    session.commit()

companies = get_all_companies()
ticker_options = [c.ticker for c in companies]

if not ticker_options:
    st.info("No companies in the database yet — run the daily pipeline at least once.")
else:
    to_add = st.selectbox("Add a company to your watchlist", ticker_options)
    if st.button("Add to watchlist"):
        company = session.query(Company).filter_by(ticker=to_add).first()
        exists = (
            session.query(Watchlist)
            .filter_by(user_id=user.user_id, company_id=company.company_id)
            .first()
        )
        if not exists:
            session.add(Watchlist(user_id=user.user_id, company_id=company.company_id))
            session.commit()
            st.success(f"Added {to_add}.")
        else:
            st.info(f"{to_add} is already on your watchlist.")

    st.divider()
    st.subheader("Your Watchlist")
    watch_rows = (
        session.query(Watchlist, Company)
        .join(Company, Company.company_id == Watchlist.company_id)
        .filter(Watchlist.user_id == user.user_id)
        .all()
    )

    if not watch_rows:
        st.info("Your watchlist is empty — add a company above.")
    else:
        for watch, company in watch_rows:
            with st.expander(f"{company.ticker} — {company.name}"):
                news_rows = get_news_for_company(company.ticker, limit=5)
                if not news_rows:
                    st.write("No recent tagged news.")
                else:
                    for news, summary in news_rows:
                        st.write(f"**[{summary.classification}]** {news.title}")
                        st.caption(summary.why_it_matters)

session.close()
