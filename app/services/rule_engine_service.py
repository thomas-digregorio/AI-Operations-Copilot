from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.core.constants import MATERIAL_CATALOG_PATH, PRICING_RULES_PATH
from app.schemas.common import WarningItem
from app.schemas.quote import QuoteRequest, QuoteValidationResponse


@dataclass
class RuleContext:
    material_catalog: pd.DataFrame
    pricing_rules: pd.DataFrame


class RuleEngineService:
    def __init__(
        self, material_catalog_path=MATERIAL_CATALOG_PATH, pricing_rules_path=PRICING_RULES_PATH
    ):
        self.material_catalog_path = material_catalog_path
        self.pricing_rules_path = pricing_rules_path

    def _load_context(self) -> RuleContext:
        material_catalog = (
            pd.read_csv(self.material_catalog_path)
            if self.material_catalog_path.exists()
            else pd.DataFrame()
        )
        pricing_rules = (
            pd.read_csv(self.pricing_rules_path)
            if self.pricing_rules_path.exists()
            else pd.DataFrame()
        )
        return RuleContext(material_catalog=material_catalog, pricing_rules=pricing_rules)

    def validate_quote(self, quote: QuoteRequest) -> QuoteValidationResponse:
        ctx = self._load_context()
        missing_fields = []
        warnings: list[WarningItem] = []
        escalation_required = False

        required = ["customer_name", "product_form", "thickness_mm", "width_mm", "qty_kg"]
        for field in required:
            if getattr(quote, field) in (None, ""):
                missing_fields.append(field)

        catalog_row = None
        if not ctx.material_catalog.empty and quote.alloy_name:
            matches = ctx.material_catalog[
                ctx.material_catalog["alloy_name"].str.lower() == quote.alloy_name.lower()
            ]
            if not matches.empty:
                catalog_row = matches.iloc[0]
            else:
                warnings.append(
                    WarningItem(
                        code="unsupported_alloy",
                        message=f"Alloy {quote.alloy_name} not found in material catalog.",
                    )
                )

        if catalog_row is not None:
            supported_forms = str(catalog_row.get("product_forms_supported", "")).lower().split(";")
            if quote.product_form and quote.product_form.lower() not in supported_forms:
                warnings.append(
                    WarningItem(
                        code="unsupported_form",
                        message=(
                            f"Product form {quote.product_form} is not supported "
                            f"for {quote.alloy_name}."
                        ),
                    )
                )

            thickness_min = float(catalog_row.get("min_thickness_mm", 0.0))
            thickness_max = float(catalog_row.get("max_thickness_mm", 1e9))
            width_min = float(catalog_row.get("min_width_mm", 0.0))
            width_max = float(catalog_row.get("max_width_mm", 1e9))

            if quote.thickness_mm is not None and not (
                thickness_min <= quote.thickness_mm <= thickness_max
            ):
                warnings.append(
                    WarningItem(
                        code="thickness_out_of_bounds",
                        message=(
                            f"Thickness {quote.thickness_mm}mm outside supported range "
                            f"{thickness_min}-{thickness_max}mm."
                        ),
                    )
                )

            if quote.width_mm is not None and not (width_min <= quote.width_mm <= width_max):
                warnings.append(
                    WarningItem(
                        code="width_out_of_bounds",
                        message=(
                            f"Width {quote.width_mm}mm outside supported range "
                            f"{width_min}-{width_max}mm."
                        ),
                    )
                )

            cert_options = str(catalog_row.get("cert_options", "")).lower().split(";")
            if quote.cert_required and quote.cert_required.lower() not in cert_options:
                warnings.append(
                    WarningItem(
                        code="cert_mismatch",
                        message=(
                            f"Requested cert {quote.cert_required} not listed "
                            "for selected alloy."
                        ),
                    )
                )

            base_lead = int(catalog_row.get("base_lead_time_days", 0))
            if (
                quote.required_lead_time_days is not None
                and quote.required_lead_time_days < base_lead
            ):
                warnings.append(
                    WarningItem(
                        code="lead_time_risk",
                        message=(
                            f"Requested lead time {quote.required_lead_time_days}d "
                            f"is below typical base {base_lead}d."
                        ),
                    )
                )

        if not ctx.pricing_rules.empty and quote.qty_kg is not None:
            moq_rows = ctx.pricing_rules[ctx.pricing_rules["rule_type"].str.lower().eq("moq")]
            if quote.alloy_name and not moq_rows.empty:
                alloy_rows = moq_rows[
                    moq_rows["alloy_name"].str.lower().eq(quote.alloy_name.lower())
                ]
                if not alloy_rows.empty:
                    moq = float(alloy_rows.iloc[0].get("min_qty_kg", 0.0))
                    if quote.qty_kg < moq:
                        warnings.append(
                            WarningItem(
                                code="below_moq",
                                message=(
                                    f"Requested quantity {quote.qty_kg}kg "
                                    f"is below MOQ {moq}kg."
                                ),
                            )
                        )

        if quote.thickness_mm is not None and quote.thickness_mm <= 0.05:
            escalation_required = True
            warnings.append(
                WarningItem(
                    code="thin_foil_review",
                    message="Thin foil request requires engineering review.",
                )
            )

        if quote.special_requirements:
            sr = quote.special_requirements.lower()
            if any(token in sr for token in ["tight tolerance", "custom", "prototype", "rush"]):
                escalation_required = True
                warnings.append(
                    WarningItem(
                        code="special_requirement_review",
                        message="Special requirements trigger engineering/sales review.",
                    )
                )

        valid = len(missing_fields) == 0 and not any(
            w.code in {"thickness_out_of_bounds", "width_out_of_bounds", "unsupported_form"}
            for w in warnings
        )

        penalty = min(0.9, (0.12 * len(missing_fields)) + (0.07 * len(warnings)))
        confidence = max(0.05, 0.95 - penalty)

        suggestions = []
        if missing_fields:
            suggestions.append("Provide missing required fields before drafting quote.")
        if escalation_required:
            suggestions.append("Escalate to engineering review queue.")

        return QuoteValidationResponse(
            request_id=quote.request_id,
            is_valid=valid,
            missing_fields=missing_fields,
            warnings=warnings,
            escalation_required=escalation_required,
            confidence=round(confidence, 3),
            suggested_actions=suggestions,
        )
