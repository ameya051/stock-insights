# PeakAgent Assignment — Flask + Postgres + Gemini

A minimal but production-ready Flask service that:
- Exposes simple REST endpoints (ping, FMP proxy, latest recommendation)
- Persists end-of-day (EOD) prices into PostgreSQL
- Runs a daily job to fetch → analyze (Gemini) → store recommendations
- Ships with Alembic migrations and Railway-friendly deployment settings

## Setup

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template and fill in your secrets:

```bash
cp .env.example .env
# edit .env with DATABASE_URL, FMP_API_KEY, GOOGLE_API_KEY, etc.
```

Run DB migrations:

```bash
alembic upgrade head
```

## Folder structure

```
.
├─ app/
│  ├─ __init__.py                # App factory, CORS, centralized blueprint registration
│  ├─ db.py                      # SQLAlchemy engine/session (psycopg v3)
│  ├─ models.py                  # ORM models: EodPrice, DailyRecommendation
│  ├─ routes/
│  │  ├─ __init__.py             # register_blueprints helper (auto-discovers blueprints)
│  │  ├─ ping.py                 # GET /api/ping
│  │  ├─ fetch_data.py           # POST /api/fmp/historical-eod (from/to in JSON body)
│  │  └─ recommendations.py      # GET /api/recommendations/latest
│  └─ services/
│     ├─ __init__.py
│     ├─ fmp_service.py          # Fetch single-day EOD from FMP
│     ├─ repository.py           # DB helpers to read/write
│     └─ llm_service.py          # Gemini analysis with JSON-only output
├─ migrations/                   # Alembic migrations
├─ scripts/
│  └─ daily_eod_analysis.py      # Daily pipeline CLI job
├─ run.py                        # Local entrypoint (respects PORT/FLASK_DEBUG)
├─ requirements.txt              # Pinned deps (Flask, SQLAlchemy, psycopg, Alembic, Gemini, Gunicorn)
├─ Procfile                      # Gunicorn command for Railway
├─ .env.example                  # Sample environment configuration
└─ README.md
```

## API endpoints

Base prefix: `/api`

- Health
	- GET `/api/ping`
		- Response: `{ "status": "ok", "message": "pong" }`

- Financial Modeling Prep proxy
	- GET `/api/fmp/historical-eod`
		- Body (JSON): `{ "from": "YYYY-MM-DD", "to": "YYYY-MM-DD", "symbol": "BTCUSD" }`
		- Returns: upstream list payload from FMP with envelope
		- Notes: does not persist; intended for ad-hoc queries

- Recommendations
	- GET `/api/recommendations/latest?symbol=BTCUSD`
		- Returns the most recent recommendation for the symbol (by trade_date then created_at)
		- 404 if none found

## Daily job: fetch → analyze → recommend

This repo includes a daily pipeline that:
- Fetches today’s BTCUSD EOD from FMP
- Saves it to Postgres (dedup by date)
- Loads the last 7 days
- Runs Gemini with a strict system prompt (JSON-only output)
- Saves a flattened recommendation into `daily_recommendations`

Prereqs:
- `DATABASE_URL` set to your Postgres URL (psycopg v3 driver is handled automatically)
- `FMP_API_KEY` set in your environment or `.env`

Run it manually:

```bash
source .venv/bin/activate
python scripts/daily_eod_analysis.py
```

Optional environment variables:
- `SYMBOL` (default: BTCUSD)
- `GEMINI_MODEL` (default: gemini-2.5-flash)

## Run locally

```bash
python run.py
```

Then visit:

- http://127.0.0.1:5000/api/ping

Expected response:

```json
{"status":"ok","message":"pong"}
```

## Technologies used

- Python 3, Flask 3
- SQLAlchemy 2 + psycopg v3 (postgresql+psycopg)
- Alembic (migrations)
- requests (HTTP client)
- Flask-Cors (CORS)
- Google Generative AI SDK (Gemini)
- Gunicorn (production WSGI server)

## How it works (high-level)

1) App factory initializes Flask, loads .env, adds CORS, and auto-registers all blueprints under `app.routes`.
2) The FMP proxy endpoint hits the FMP API (with API key) and returns historical EOD data for requested range.
3) The daily CLI job fetches today’s EOD, upserts into `eod_prices`, loads last 7 days, calls Gemini with a JSON-only system prompt, and stores the recommendation into `daily_recommendations`.
4) The recommendations endpoint returns the most recent saved recommendation for a symbol.

## Database migrations (Alembic)

Initialize and run migrations from the project root:

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql://USER:PASSWORD@HOST/DBNAME"
alembic upgrade head

## Deploying to Railway

- Procfile starts Gunicorn: `web: gunicorn -w 1 -k gthread --threads 2 --max-requests 200 --max-requests-jitter 50 -t 60 -b 0.0.0.0:${PORT:-5000} run:app`
- Set env vars in Railway: `DATABASE_URL`, `FMP_API_KEY`, and `GOOGLE_API_KEY` (or `GEMINI_API_KEY`).
- Trial plan friendly: 1 worker, 2 threads.
