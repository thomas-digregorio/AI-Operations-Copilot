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
        self,
        alloy_name: str | None,
        product_form: str | None,
        qty_kg: float | None,
        thickness_mm: float | None = None,
        width_mm: float | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        df = self._load_history()
        if df.empty:
            return []

        df = df.copy()
        df["score"] = 0.0

        if alloy_name:
            df["score"] += df["alloy_name"].str.lower().eq(alloy_name.lower()).astype(float) * 0.45

        if product_form:
            df["score"] += (
                df["product_form"].str.lower().eq(product_form.lower()).astype(float) * 0.20
            )

        if qty_kg is not None and "qty_kg" in df.columns:
            qty_delta = (df["qty_kg"] - qty_kg).abs().fillna(1e9)
            df["score"] += qty_delta.apply(lambda d: 0.15 * math.exp(-float(d) / 800.0))

        if thickness_mm is not None and "thickness_mm" in df.columns:
            th_delta = (df["thickness_mm"] - thickness_mm).abs().fillna(1e9)
            df["score"] += th_delta.apply(lambda d: 0.10 * math.exp(-float(d) / 0.25))

        if width_mm is not None and "width_mm" in df.columns:
            wd_delta = (df["width_mm"] - width_mm).abs().fillna(1e9)
            df["score"] += wd_delta.apply(lambda d: 0.10 * math.exp(-float(d) / 250.0))

        df = df.sort_values(["score", "quote_date"], ascending=[False, False])
        out = df.head(top_k).copy()
        out["similarity_score"] = out["score"].round(4)
        out.drop(columns=["score"], inplace=True, errors="ignore")
        return out.to_dict(orient="records")
