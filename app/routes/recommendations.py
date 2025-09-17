from typing import Optional, Any
from flask import Blueprint, jsonify, request
from sqlalchemy import desc, select
from app.db import SessionLocal
from app.models import DailyRecommendation

recs_bp = Blueprint("recommendations", __name__)


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    return float(x)


@recs_bp.get("/recommendations/latest")
def latest_recommendation():
    symbol = request.args.get("symbol", "BTCUSD")

    with SessionLocal() as session:
        stmt = select(DailyRecommendation).where(DailyRecommendation.symbol == symbol)
        stmt = stmt.order_by(
            desc(DailyRecommendation.trade_date), desc(DailyRecommendation.created_at)
        ).limit(1)
        rec = session.scalars(stmt).first()

    if not rec:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": "No recommendation found for criteria",
                    "symbol": symbol,
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "id": rec.id,
                "symbol": rec.symbol,
                "trade_date": rec.trade_date.isoformat(),
                "model_name": rec.model_name,
                "recommendation": rec.recommendation,
                "rationale": rec.rationale,
                "change_percent": _to_float(getattr(rec, "change_percent", None)),
                "window_days": rec.window_days,
                "created_at": rec.created_at.isoformat(),
            }
        ),
        200,
    )
