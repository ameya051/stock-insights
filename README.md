# Simple Flask API

A minimal, well-structured Flask REST API with a single `GET /ping` endpoint.

## Structure

- `app/__init__.py` – App factory and blueprint registration
- `app/routes/ping.py` – `GET /ping` endpoint
- `run.py` – Local entry point
- `requirements.txt` – Python dependencies

## Setup

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

Then visit:

- http://127.0.0.1:5000/ping

Expected response:

```json
{"status":"ok","message":"pong"}
```

## Notes

- The server binds to `0.0.0.0:5000` for container/VM friendliness. Set `FLASK_ENV` or adjust `debug` in `run.py` as needed.

## Database migrations (Alembic)

Initialize and run migrations from the project root:

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql://USER:PASSWORD@HOST/DBNAME"  # Neon or local
# Autogenerate migration from current models
alembic revision --autogenerate -m "init"
# Apply latest
alembic upgrade head
```
