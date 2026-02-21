from __future__ import annotations

import random

import numpy as np
import pandas as pd
import pytest

from app.core.constants import STEEL_RAW_DIR
from app.pipelines.build_synthetic_quote_data import build_material_catalog, build_pricing_rules


@pytest.fixture(autouse=True)
def set_seed():
    random.seed(42)
    np.random.seed(42)


@pytest.fixture
def ensure_rule_data(tmp_path):
    material_path = tmp_path / "material_catalog.csv"
    pricing_path = tmp_path / "pricing_rules.csv"
    build_material_catalog().to_csv(material_path, index=False)
    build_pricing_rules().to_csv(pricing_path, index=False)
    return material_path, pricing_path


@pytest.fixture
def synthetic_steel_dataset(tmp_path):
    rows = 260
    feature_cols = 27
    label_cols = 7
    X = np.random.rand(rows, feature_cols)

    labels = np.zeros((rows, label_cols))
    y = np.random.randint(0, label_cols, size=rows)
    labels[np.arange(rows), y] = 1

    df = pd.DataFrame(np.concatenate([X, labels], axis=1))
    path = tmp_path / "Faults.NNA.csv"
    df.to_csv(path, index=False, header=False)
    return path


@pytest.fixture
def staged_steel_dataset(synthetic_steel_dataset):
    STEEL_RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = STEEL_RAW_DIR / "Faults.NNA.csv"
    target.write_text(synthetic_steel_dataset.read_text(encoding="utf-8"), encoding="utf-8")
    return target
