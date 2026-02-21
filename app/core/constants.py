from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
VECTOR_DIR = ARTIFACTS_DIR / "vector_index"
MODELS_DIR = ARTIFACTS_DIR / "models"
METRICS_DIR = ARTIFACTS_DIR / "metrics"
EVALS_DIR = ARTIFACTS_DIR / "evals"

ULBRICH_PUBLIC_DIR = RAW_DATA_DIR / "ulbrich_public"
INTERNAL_MOCK_DOCS_DIR = RAW_DATA_DIR / "internal_mock_docs"
STEEL_RAW_DIR = RAW_DATA_DIR / "steel_plates_faults"

MATERIAL_CATALOG_PATH = PROCESSED_DATA_DIR / "material_catalog.csv"
PRICING_RULES_PATH = PROCESSED_DATA_DIR / "pricing_rules.csv"
QUOTE_HISTORY_PATH = PROCESSED_DATA_DIR / "quote_history_synthetic.csv"

DEFAULT_MODEL_FILENAME = "steel_fault_xgb.joblib"
DEFAULT_MODEL_PATH = MODELS_DIR / DEFAULT_MODEL_FILENAME
DEFAULT_METRICS_PATH = METRICS_DIR / "steel_fault_metrics.json"
DEFAULT_FEATURES_PATH = MODELS_DIR / "steel_fault_feature_columns.json"
