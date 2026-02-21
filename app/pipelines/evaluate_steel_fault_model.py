from __future__ import annotations

import json

from app.core.constants import DEFAULT_METRICS_PATH, EVALS_DIR


def main() -> None:
    if not DEFAULT_METRICS_PATH.exists():
        raise FileNotFoundError("Metrics file not found. Run training first.")

    with DEFAULT_METRICS_PATH.open("r", encoding="utf-8") as f:
        metrics = json.load(f)

    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EVALS_DIR / "steel_eval_summary.json"
    summary_payload = {
        "macro_f1": metrics.get("macro_f1", 0.0),
        "label_columns": metrics.get("label_columns", []),
        "has_confusion_matrix": bool(metrics.get("confusion_matrix")),
    }
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print(f"Wrote evaluation summary to {summary_path}")
    print(summary_payload)


if __name__ == "__main__":
    main()
