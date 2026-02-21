from __future__ import annotations

import math

import pandas as pd

from app.core.constants import QUOTE_HISTORY_PATH


class QuoteHistoryService:
    def __init__(self, history_path=QUOTE_HISTORY_PATH):
        self.history_path = history_path

    def _load_history(self) -> pd.DataFrame:
        if not self.history_path.exists():
            return pd.DataFrame()
        return pd.read_csv(self.history_path)

    def find_similar_quotes(
        self, alloy_name: str | None, product_form: str | None, qty_kg: float | None, top_k: int = 5
    ) -> list[dict]:
        df = self._load_history()
        if df.empty:
            return []

        if alloy_name:
            df = df[df["alloy_name"].str.lower() == alloy_name.lower()]
        if product_form:
            df = df[df["product_form"].str.lower() == product_form.lower()]
        if df.empty:
            return []

        if qty_kg is not None and "qty_kg" in df.columns:
            df = df.assign(distance=(df["qty_kg"] - qty_kg).abs())
        else:
            df = df.assign(distance=0.0)

        df = df.sort_values(["distance", "quote_date"], ascending=[True, False])
        out = df.head(top_k).copy()
        out["similarity_score"] = out["distance"].apply(lambda d: round(math.exp(-d / 500.0), 4))
        return out.to_dict(orient="records")
