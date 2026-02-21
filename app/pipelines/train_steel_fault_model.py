from __future__ import annotations

from pathlib import Path

import requests

from app.core.constants import STEEL_RAW_DIR
from app.services.steel_model_service import SteelModelService

DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00198/Faults.NNA"


def ensure_dataset() -> Path:
    STEEL_RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = STEEL_RAW_DIR / "Faults.NNA.csv"
    if target.exists():
        return target

    response = requests.get(DATA_URL, timeout=60)
    response.raise_for_status()
    target.write_text(response.text, encoding="utf-8")
    return target


def main() -> None:
    dataset = ensure_dataset()
    print(f"Using dataset: {dataset}")
    service = SteelModelService()
    result = service.train(dataset_path=str(dataset))
    print(result)


if __name__ == "__main__":
    main()
