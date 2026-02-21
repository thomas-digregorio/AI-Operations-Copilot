from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import QuoteHistoryRecord


def replace_quote_history_records(db: Session, rows: list[dict]) -> int:
    db.query(QuoteHistoryRecord).delete(synchronize_session=False)
    db.flush()
    for row in rows:
        db.add(
            QuoteHistoryRecord(
                quote_id=str(row.get("quote_id", "")),
                quote_date=str(row.get("quote_date", "")),
                customer_name=row.get("customer_name"),
                alloy_name=row.get("alloy_name"),
                product_form=row.get("product_form"),
                thickness_mm=_float_or_none(row.get("thickness_mm")),
                width_mm=_float_or_none(row.get("width_mm")),
                qty_kg=_float_or_none(row.get("qty_kg")),
                lead_time_days=_int_or_none(row.get("lead_time_days")),
                cert_required=row.get("cert_required"),
                price_total_usd=_float_or_none(row.get("price_total_usd")),
                status=row.get("status"),
            )
        )
    db.commit()
    return len(rows)


def list_quote_history_records(db: Session) -> list[dict]:
    rows = db.query(QuoteHistoryRecord).all()
    return [
        {
            "quote_id": row.quote_id,
            "quote_date": row.quote_date,
            "customer_name": row.customer_name,
            "alloy_name": row.alloy_name,
            "product_form": row.product_form,
            "thickness_mm": row.thickness_mm,
            "width_mm": row.width_mm,
            "qty_kg": row.qty_kg,
            "lead_time_days": row.lead_time_days,
            "cert_required": row.cert_required,
            "price_total_usd": row.price_total_usd,
            "status": row.status,
        }
        for row in rows
    ]


def _float_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
