from __future__ import annotations

from app.core.constants import INTERNAL_MOCK_DOCS_DIR

DOCS = {
    "Sales_Quote_SOP_v1.md": """
# Synthetic Internal Document
# Sales Quote SOP v1

This synthetic policy defines quote intake workflow:
1. Validate required fields (customer, alloy/form, dimensions, quantity).
2. Run deterministic rules for MOQ, dimensional fit, and cert compatibility.
3. Flag thin foil (<0.05mm) and unusual special requirements for engineering review.
4. Draft quote package with assumptions and citation references.
""",
    "Lead_Time_and_MOQ_Policy_v1.md": """
# Synthetic Internal Document
# Lead Time and MOQ Policy v1

- Base lead times vary by alloy family and mill load.
- MOQ thresholds:
  - 316L: 150kg
  - 304: 200kg
  - 17-7PH: 120kg
- Rush requests under base lead time require escalation.
""",
    "Certifications_and_Compliance_Policy.md": """
# Synthetic Internal Document
# Certifications and Compliance Policy

- Certification must be compatible with selected alloy and product form.
- Unsupported cert requests require alternate recommendation or escalation.
- Claims must reference source docs and deterministic policy rules.
""",
    "Packaging_and_Shipping_Constraints.md": """
# Synthetic Internal Document
# Packaging and Shipping Constraints

- Foil orders use protective reel packaging when width < 300mm.
- Export shipments require additional compliance checks.
- Non-standard packaging can increase lead time by 3-7 days.
""",
    "Escalation_Rules_for_Engineering_Review.md": """
# Synthetic Internal Document
# Escalation Rules for Engineering Review

Escalate when:
- thickness <= 0.05mm
- cert mismatch or uncertain standards mapping
- customer asks for custom tolerance stack not in catalog
- lead time request under base threshold
""",
    "Customer_Quote_Request_Template.md": """
# Synthetic Internal Document
# Customer Quote Request Template

Required fields:
- Customer name
- Alloy + form
- Thickness + width
- Quantity (kg)
Optional:
- Certification
- Temper
- Required lead time
- Special requirements
""",
}

CSV_CONTENT = """rule_id,rule_type,alloy_name,min_qty_kg,price_per_kg_low,price_per_kg_high
PR-316L,price_band,316L,150,7.50,11.80
PR-304,price_band,304,200,4.40,7.20
PR-17-7PH,price_band,17-7PH,120,9.80,15.40
"""


def main() -> None:
    INTERNAL_MOCK_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in DOCS.items():
        path = INTERNAL_MOCK_DOCS_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
    (INTERNAL_MOCK_DOCS_DIR / "Pricing_Guidelines_Internal_v1.csv").write_text(
        CSV_CONTENT, encoding="utf-8"
    )
    print(f"Wrote {len(DOCS) + 1} synthetic internal mock docs to {INTERNAL_MOCK_DOCS_DIR}")


if __name__ == "__main__":
    main()
