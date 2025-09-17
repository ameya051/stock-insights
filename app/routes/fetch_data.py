import os
from datetime import date
import requests
from flask import Blueprint, jsonify, request

fmp_bp = Blueprint("fmp", __name__)


@fmp_bp.get("/fmp/historical-eod")
def historical_eod():
    """Fetch historical EOD data from FMP for the given date window.

    Request JSON body:
    {
      "from": "YYYY-MM-DD",
      "to": "YYYY-MM-DD",
      "symbol": "BTCUSD"    # optional, defaults to BTCUSD
    }

    Returns the upstream list payload as-is in data.
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

    body = request.get_json(silent=True) or {}
    from_str = body.get("from")
    to_str = body.get("to")
    symbol = (body.get("symbol") or "BTCUSD").strip() or "BTCUSD"

    if not isinstance(from_str, str) or not isinstance(to_str, str):
        return (
            jsonify({
                "error": "invalid_request",
                "message": "Body must include 'from' and 'to' as ISO YYYY-MM-DD strings",
            }),
            400,
        )

    try:
        from_dt = date.fromisoformat(from_str)
        to_dt = date.fromisoformat(to_str)
    except ValueError:
        return (
            jsonify({
                "error": "invalid_date",
                "message": "Dates must be ISO YYYY-MM-DD",
            }),
            400,
        )

    if from_dt > to_dt:
        return (
            jsonify({
                "error": "invalid_range",
                "message": "'from' date cannot be after 'to' date",
            }),
            400,
        )

    base_url = "https://financialmodelingprep.com/stable/historical-price-eod/full"
    params = {
        "symbol": symbol,
        "from": from_dt.isoformat(),
        "to": to_dt.isoformat(),
        "apikey": api_key,
    }

    try:
        resp = requests.get(base_url, params=params, timeout=20)
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

    # Validate upstream payload (expect a list)
    if not isinstance(payload, list):
        return (
            jsonify(
                {
                    "error": "invalid_upstream_payload",
                    "message": "Expected a list",
                }
            ),
            502,
        )

    return jsonify({
        "status": "ok",
        "symbol": symbol,
        "from": from_dt.isoformat(),
        "to": to_dt.isoformat(),
        "count": len(payload),
        "data": payload,
    }), 200
