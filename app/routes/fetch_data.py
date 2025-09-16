import os
from datetime import date, timedelta
from decimal import Decimal
import requests
from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.models import EodPrice

fmp_bp = Blueprint("fmp", __name__)


@fmp_bp.get("/fmp/historical-eod")
def historical_eod():
    """Proxy endpoint to fetch historical EOD data for BTCUSD from FMP.
    Requires FMP_API_KEY in environment.
    """
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return (
            jsonify(
                {
                    "error": "missing_api_key",
                    "message": "Set FMP_API_KEY in environment",
                }
            ),
            400,
        )

    # Fetch only today's EOD (API returns an array with one object)
    today = date.today()
    base_url = (
        "https://financialmodelingprep.com/stable/historical-price-eod/full"
        f"?symbol=BTCUSD&from={today:%Y-%m-%d}&to={today:%Y-%m-%d}&apikey="
        + api_key
    )

    try:
        resp = requests.get(base_url, timeout=20)
        resp.raise_for_status()
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else 502
        return (
            jsonify(
                {"error": "upstream_http_error", "status": status, "message": str(e)}
            ),
            status,
        )
    except requests.RequestException as e:
        return jsonify({"error": "upstream_request_failed", "message": str(e)}), 502

    # Parse upstream JSON
    try:
        payload = resp.json()
    except ValueError:
        return jsonify({"error": "invalid_upstream_json"}), 502

    # Validate upstream payload (expect an array with one object)
    if not isinstance(payload, list) or not payload:
        return (
            jsonify(
                {
                    "error": "invalid_upstream_payload",
                    "message": "Expected a non-empty list",
                }
            ),
            502,
        )

    r = payload[0]
    ds = r.get("date")
    if not isinstance(ds, str):
        return (
            jsonify(
                {"error": "invalid_upstream_date", "message": "Missing or invalid date"}
            ),
            502,
        )

    try:
        trade_dt = date.fromisoformat(ds)
    except ValueError:
        return (
            jsonify(
                {
                    "error": "invalid_upstream_date",
                    "message": "Date must be ISO YYYY-MM-DD",
                }
            ),
            502,
        )

    symbol = r.get("symbol") or "BTCUSD"

    with SessionLocal() as session:
        # Skip insert if a row already exists for the same symbol+date
        exists = session.execute(
            select(EodPrice.id).where(
                EodPrice.symbol == symbol,
                EodPrice.trade_date == trade_dt,
            )
        ).first()
        if exists:
            return (
                jsonify(
                    {
                        "status": "ok",
                        "inserted": 0,
                        "skipped": 1,
                        "reason": "already_exists",
                        "date": trade_dt.isoformat(),
                        "data": [r],
                    }
                ),
                409,
            )

        row = EodPrice(
            symbol=symbol,
            trade_date=trade_dt,
            open=Decimal(str(r.get("open"))) if r.get("open") is not None else None,
            high=Decimal(str(r.get("high"))) if r.get("high") is not None else None,
            low=Decimal(str(r.get("low"))) if r.get("low") is not None else None,
            close=Decimal(str(r.get("close"))) if r.get("close") is not None else None,
            vwap=Decimal(str(r.get("vwap"))) if r.get("vwap") is not None else None,
            volume=r.get("volume"),
            change_abs=(
                Decimal(str(r.get("change"))) if r.get("change") is not None else None
            ),
            change_percent=(
                Decimal(str(r.get("changePercent")))
                if r.get("changePercent") is not None
                else None
            ),
        )
        try:
            session.add(row)
            session.commit()
        except IntegrityError:
            session.rollback()
            return (
                jsonify(
                    {
                        "status": "ok",
                        "inserted": 0,
                        "skipped": 1,
                        "reason": "already_exists",
                        "date": trade_dt.isoformat(),
                        "data": [r],
                    }
                ),
                409,
            )

    return jsonify({"status": "ok", "inserted": 1, "data": [r]}), 201
