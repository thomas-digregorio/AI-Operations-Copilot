from __future__ import annotations

import numpy as np

from app.core.constants import STEEL_RAW_DIR
from app.services.steel_model_service import FEATURE_COLUMNS, LABEL_COLUMNS, SteelModelService


def main() -> None:
    service = SteelModelService()
    df = service.load_raw_dataset()

    X = df[FEATURE_COLUMNS].copy()
    y_idx = df[LABEL_COLUMNS].values.argmax(axis=1)
    class_names = [LABEL_COLUMNS[i] for i in y_idx]

    enriched = X.copy()
    enriched["fault_class"] = class_names
    enriched["line_id"] = np.random.choice(["L1", "L2", "L3"], size=len(enriched))
    enriched["shift"] = np.random.choice(["A", "B", "C"], size=len(enriched))
    enriched["operator_tenure_months"] = np.random.randint(1, 120, size=len(enriched))

    out_path = STEEL_RAW_DIR.parent.parent / "business_enriched" / "steel_faults_enriched.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_path, index=False)
    print(f"Wrote business-enriched dataset to {out_path}")


if __name__ == "__main__":
    main()
