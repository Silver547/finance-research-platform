# AI Finance Research Platform

A free-first, Bloomberg/AlphaSense-style research assistant. It ingests news, filings,
prices, and macro data every day, has an AI layer summarize and explain what happened
and why it matters, stores everything in a database + vector index, and shows it all
in a Streamlit dashboard with a RAG chatbot. It is a **research assistant, not a
signal generator** — it never tells you to buy or sell anything.

This is a **working starter implementation**, not just a plan. Phases 1–4 from the
roadmap (dashboard, news ingestion, AI summarization, RAG chatbot) are fully wired up
and runnable today. Phases 5–9 (deep company filings, full macro coverage, production
deployment) have their tables, folder structure, and one working example each, ready
for you to extend — see "What's stubbed vs. what's complete" below.

---

## 1. Quick Start (5 minutes)

```bash
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your environment
cp .env.example .env
# Now open .env and add at least ONE free LLM key:
#   - Get a free Google AI Studio key: https://aistudio.google.com/  (recommended)
#   - OR a free OpenRouter key: https://openrouter.ai/
#   - OR install Ollama locally (https://ollama.com) and set LLM_PROVIDER=ollama

# 4. Seed reference data (industries)
python scripts_seed_industries.py

# 5. Run the full daily pipeline once (fetches news, tags it, analyzes it,
#    fetches macro data, builds the search index, writes a daily digest)
python pipelines/orchestrator.py

# 6. Launch the dashboard
streamlit run dashboard/Home.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`). You should see
today's news with AI analysis, and a sidebar with Market Overview, Sectors, Company,
Macro, Watchlist, and AI Chat pages.

**First run will be slow** — it's calling a free-tier LLM for every headline it
finds. Free tiers are rate-limited (e.g. Gemini free tier is roughly 15
requests/minute), so if you have a lot of feeds configured, step 5 can take a
few minutes. That's expected and only happens once per new headline.

---

## 2. What's Complete vs. What's Stubbed

**Fully working today:**
- News ingestion from free RSS feeds (`pipelines/news/fetch_rss.py`)
- Duplicate detection (`pipelines/news/dedup.py`)
- AI tagging of companies/industries per headline (`agents/tagging_agent.py`)
- AI summarization + "why it matters" + impact/risk/opportunity analysis
  (`agents/impact_agent.py`)
- Free World Bank macro data ingestion (`pipelines/macro/fetch_macro.py`)
- Stock price + technical indicators via yfinance (`pipelines/stocks/fetch_prices.py`)
- Vector index of AI summaries + RAG chatbot (`rag/build_index.py`, `rag/chat_engine.py`)
- Daily/weekly/monthly digest generation (`agents/report_agent.py`)
- Full Streamlit dashboard: Home, Market Overview, Sectors, Company, Macro,
  Watchlist, AI Chat
- GitHub Actions workflows for daily/weekly/monthly automation
- SQLite by default (zero setup); swap to Postgres/Supabase by changing one
  env var

**Tables exist, ingestion is your next step (by design — these need your own
account/API keys or are genuinely bigger pieces of work):**
- `financial_statements`, `ratios`, `ownership`, `corporate_actions` — wire up
  SEC EDGAR (US) and NSE/BSE (India) fetchers following the exact pattern in
  `pipelines/news/fetch_rss.py`. SEC EDGAR has a clean free JSON API
  (`https://data.sec.gov/`); NSE/BSE need unofficial wrapper libraries
  (`nsepython`, `bsedata`) and should be rate-limited politely.
- SWOT/moat analysis, competitor comparison — same agent pattern as
  `agents/impact_agent.py`, just a different prompt template and a company
  page instead of a news row as input.
- FastAPI backend (`backend/api/`) — the dashboard currently reads the DB
  directly, which is simpler for a solo user. Add this layer only if you want
  a separate mobile client or multiple users later.

I deliberately did not fake these with placeholder/mock data — better to leave
them as a clear next step than to ship something that looks done but isn't real.

---

## 3. Project Structure

```
finance-research-platform/
├── backend/            # DB models + session (SQLAlchemy) + optional FastAPI layer
├── pipelines/           # Ingestion: news, macro, stocks, (filings — stub)
├── agents/              # LLM-powered steps: tagging, impact analysis, reports
├── rag/                 # Embeddings + Chroma vector index + chat engine
├── prompts/             # Versioned prompt templates used by the agents
├── dashboard/           # Streamlit app (Home.py + pages/)
├── database/            # Reference schema.sql (Postgres dialect)
├── config/              # settings.py — all configuration in one place
├── docker/              # Dockerfile + docker-compose.yml
├── .github/workflows/   # Daily/weekly/monthly automation
├── tests/               # Unit tests for dedup + impact agent validation
├── scripts_seed_industries.py
├── requirements.txt
└── .env.example
```

---

## 4. Configuration

Everything is controlled from `config/settings.py` (reads `.env`). Key settings:

- `TRACKED_TICKERS` — the companies you actually follow. Edit this list.
- `TRACKED_INDUSTRIES` — the sectors you want pages for. Edit this list.
- `NEWS_FEEDS` — dict of RSS feeds to pull from. Add/remove freely.
- `LLM_PROVIDER` — `gemini` | `openrouter` | `ollama`. Gemini free tier is the
  recommended default (huge context window, generous free quota).
- `DATABASE_URL` — defaults to local SQLite. Point it at a Supabase/Postgres
  connection string when you're ready to deploy.

---

## 5. Running the Daily Pipeline on Autopilot

The included GitHub Actions workflow (`.github/workflows/daily_pipeline.yml`)
runs the whole pipeline every day automatically, for free, using GitHub's
2,000 free CI minutes/month:

1. Push this repo to GitHub.
2. In your repo settings → Secrets and variables → Actions, add:
   - `GOOGLE_AI_STUDIO_KEY` (or `OPENROUTER_API_KEY`)
   - `DATABASE_URL` (if you've moved to Supabase/Postgres — otherwise the
     workflow uses a fresh SQLite file each run and uploads it as a build
     artifact, which works but means the dashboard needs to run somewhere
     that shares that same file/DB for continuity — see note below)
3. That's it — the workflow runs on its schedule, and you can also trigger it
   manually from the Actions tab (`workflow_dispatch`).

**Important note on persistence:** GitHub Actions runners are ephemeral —
a fresh SQLite file per run won't accumulate history. For real day-over-day
persistence, either:
- Point `DATABASE_URL` at a free **Supabase Postgres** database (recommended —
  it's free, persistent, and this codebase already speaks SQLAlchemy so no
  code changes are needed, only the connection string), or
- Have the workflow commit the updated `finance_platform.db` back to the repo
  after each run (simple but not ideal for a growing binary file in git).

Supabase is the right free tool for this — sign up, create a project, and
copy its Postgres connection string into `DATABASE_URL`.

---

## 6. Running with Docker

```bash
cd docker
docker compose up dashboard        # starts the Streamlit dashboard on :8501
docker compose run pipeline        # runs the daily pipeline once
```

---

## 7. Running Tests

```bash
pip install pytest
pytest tests/
```

---

## 8. Legal Notes (read before you rely on this for real decisions)

- The AI layer stores **your own AI-generated summaries**, never full article
  text — this keeps the vector store and dashboard copyright-clean by
  construction.
- `yfinance` and NSE/BSE scraping sit in a legal gray area for automated use —
  fine for personal research at this scale, but don't redistribute the raw
  data or scrape aggressively (the code already avoids re-fetching
  already-stored items).
- This tool is for research and education. It is explicitly designed to never
  output buy/sell recommendations — keep it that way if you extend it.

---

## 9. Next Steps

1. Run the quick start above and confirm you see news + AI analysis on the
   Home page.
2. Add your real tracked tickers/industries in `config/settings.py`.
3. Wire up SEC EDGAR filings ingestion (biggest single upgrade to Company
   Intelligence) — follow the pattern in `pipelines/news/fetch_rss.py`.
4. Move to Supabase Postgres once you want the daily pipeline to run
   unattended via GitHub Actions with real persistence.
5. Deploy the dashboard for free on Streamlit Community Cloud, pointing it at
   the same Supabase database.
