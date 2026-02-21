from __future__ import annotations

import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

from app.core.constants import (
    MATERIAL_CATALOG_PATH,
    PRICING_RULES_PATH,
    PROCESSED_DATA_DIR,
    QUOTE_HISTORY_PATH,
)


def build_material_catalog() -> pd.DataFrame:
    rows = [
        {
            "material_id": "MAT-316L-FOIL",
            "alloy_name": "316L",
            "alloy_family": "austenitic_stainless",
            "uns_number": "S31603",
            "product_forms_supported": "foil;sheet;strip",
            "min_thickness_mm": 0.01,
            "max_thickness_mm": 3.0,
            "min_width_mm": 5,
            "max_width_mm": 1000,
            "common_applications": "medical;electronics;chemical",
            "cert_options": "ASTM_A240;EN_10204_3.1;RoHS",
            "base_lead_time_days": 21,
            "is_active": True,
        },
        {
            "material_id": "MAT-304-SHEET",
            "alloy_name": "304",
            "alloy_family": "austenitic_stainless",
            "uns_number": "S30400",
            "product_forms_supported": "sheet;strip",
            "min_thickness_mm": 0.2,
            "max_thickness_mm": 6.0,
            "min_width_mm": 20,
            "max_width_mm": 1500,
            "common_applications": "food;appliance;architecture",
            "cert_options": "ASTM_A240;EN_10204_3.1",
            "base_lead_time_days": 14,
            "is_active": True,
        },
        {
            "material_id": "MAT-17-7PH-STRIP",
            "alloy_name": "17-7PH",
            "alloy_family": "precipitation_hardening",
            "uns_number": "S17700",
            "product_forms_supported": "strip;sheet",
            "min_thickness_mm": 0.05,
            "max_thickness_mm": 2.5,
            "min_width_mm": 10,
            "max_width_mm": 1200,
            "common_applications": "spring;aerospace;energy",
            "cert_options": "AMS5528;EN_10204_3.1",
            "base_lead_time_days": 28,
            "is_active": True,
        },
    ]
    return pd.DataFrame(rows)


def build_pricing_rules() -> pd.DataFrame:
    rows = [
        {"rule_id": "MOQ-316L", "rule_type": "moq", "alloy_name": "316L", "min_qty_kg": 150},
        {"rule_id": "MOQ-304", "rule_type": "moq", "alloy_name": "304", "min_qty_kg": 200},
        {"rule_id": "MOQ-17-7PH", "rule_type": "moq", "alloy_name": "17-7PH", "min_qty_kg": 120},
        {
            "rule_id": "PB-316L",
            "rule_type": "price_band",
            "alloy_name": "316L",
            "price_per_kg_low": 7.5,
            "price_per_kg_high": 11.8,
        },
        {
            "rule_id": "PB-304",
            "rule_type": "price_band",
            "alloy_name": "304",
            "price_per_kg_low": 4.4,
            "price_per_kg_high": 7.2,
        },
        {
            "rule_id": "PB-17-7PH",
            "rule_type": "price_band",
            "alloy_name": "17-7PH",
            "price_per_kg_low": 9.8,
            "price_per_kg_high": 15.4,
        },
    ]
    return pd.DataFrame(rows)


def build_quote_history(rows: int = 3000) -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)

    alloys = ["316L", "304", "17-7PH"]
    forms = {
        "316L": ["foil", "sheet", "strip"],
        "304": ["sheet", "strip"],
        "17-7PH": ["strip", "sheet"],
    }
    certs = {
        "316L": ["ASTM_A240", "EN_10204_3.1", "RoHS"],
        "304": ["ASTM_A240", "EN_10204_3.1"],
        "17-7PH": ["AMS5528", "EN_10204_3.1"],
    }

    base = date.today() - timedelta(days=730)
    out = []
    for i in range(rows):
        alloy = random.choice(alloys)
        form = random.choice(forms[alloy])
        qty = float(np.random.lognormal(mean=5.4, sigma=0.6))
        thickness = round(max(0.01, np.random.normal(0.2, 0.15)), 4)
        width = round(float(np.random.uniform(20, 1200)), 2)
        lead_days = int(np.random.choice([10, 14, 21, 28, 35]))
        cert = random.choice(certs[alloy])
        quote_date = base + timedelta(days=i % 730)
        out.append(
            {
                "quote_id": f"Q-{100000 + i}",
                "quote_date": quote_date.isoformat(),
                "customer_name": f"Customer-{random.randint(1, 240)}",
                "alloy_name": alloy,
                "product_form": form,
                "thickness_mm": thickness,
                "width_mm": width,
                "qty_kg": round(qty, 2),
                "lead_time_days": lead_days,
                "cert_required": cert,
                "price_total_usd": round(qty * float(np.random.uniform(5.5, 14.8)), 2),
                "status": random.choice(["won", "lost", "pending"]),
            }
        )
    return pd.DataFrame(out)


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    mat = build_material_catalog()
    prc = build_pricing_rules()
    hist = build_quote_history(rows=3000)

    mat.to_csv(MATERIAL_CATALOG_PATH, index=False)
    prc.to_csv(PRICING_RULES_PATH, index=False)
    hist.to_csv(QUOTE_HISTORY_PATH, index=False)

    print(f"Wrote {MATERIAL_CATALOG_PATH}")
    print(f"Wrote {PRICING_RULES_PATH}")
    print(f"Wrote {QUOTE_HISTORY_PATH} ({len(hist)} rows)")


if __name__ == "__main__":
    main()
