from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st

DEFAULT_FEATURES = {
    "X_Minimum": 42,
    "X_Maximum": 62,
    "Y_Minimum": 15,
    "Y_Maximum": 30,
    "Pixels_Areas": 230,
    "X_Perimeter": 45,
    "Y_Perimeter": 33,
    "Sum_of_Luminosity": 8500,
    "Minimum_of_Luminosity": 20,
    "Maximum_of_Luminosity": 140,
    "Length_of_Conveyer": 1200,
    "TypeOfSteel_A300": 1,
    "TypeOfSteel_A400": 0,
    "Steel_Plate_Thickness": 75,
    "Edges_Index": 0.4,
    "Empty_Index": 0.1,
    "Square_Index": 0.2,
    "Outside_X_Index": 0.15,
    "Edges_X_Index": 0.3,
    "Edges_Y_Index": 0.25,
    "Outside_Global_Index": 0.1,
    "LogOfAreas": 2.2,
    "Log_X_Index": 1.1,
    "Log_Y_Index": 1.0,
    "Orientation_Index": 0.12,
    "Luminosity_Index": 0.35,
    "SigmoidOfAreas": 0.66,
}
FEATURE_PRESETS = {
    "Nominal strip line": DEFAULT_FEATURES,
    "High-luminosity anomaly": {
        **DEFAULT_FEATURES,
        "Sum_of_Luminosity": 24500,
        "Maximum_of_Luminosity": 190,
        "LogOfAreas": 3.1,
        "SigmoidOfAreas": 0.92,
    },
    "Thin profile variation": {
        **DEFAULT_FEATURES,
        "Steel_Plate_Thickness": 35,
        "Edges_Index": 0.73,
        "Outside_X_Index": 0.42,
        "Orientation_Index": 0.37,
    },
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap");
        :root {
            --steel-ink: #1a2733;
            --steel-slate: #344a5d;
            --steel-teal: #1b6b6f;
            --steel-ice: #e6f0f4;
            --steel-amber: #f0a83a;
            --steel-alert: #b33f3f;
            --steel-card: rgba(255, 255, 255, 0.92);
        }
        html, body, [class*="css"]  {
            font-family: "Manrope", sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 8%, rgba(27, 107, 111, 0.22), transparent 38%),
                radial-gradient(circle at 88% 0%, rgba(240, 168, 58, 0.2), transparent 42%),
                linear-gradient(145deg, #f7fbfd 0%, #edf3f7 45%, #f8fbfc 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(190deg, #f8fbfc 0%, #edf2f5 100%);
            border-right: 1px solid rgba(52, 74, 93, 0.15);
        }
        .hero-panel {
            border: 1px solid rgba(26, 39, 51, 0.12);
            background: linear-gradient(120deg, #ffffff 0%, #f2f8fb 100%);
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 16px 30px rgba(26, 39, 51, 0.08);
            animation: fadeSlide 0.5s ease-out;
        }
        .hero-title {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--steel-ink);
            margin-bottom: 0.25rem;
        }
        .hero-sub {
            color: var(--steel-slate);
            font-size: 0.96rem;
            margin: 0;
        }
        .status-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.2rem 0.65rem;
            margin-right: 0.45rem;
            margin-bottom: 0.3rem;
            border: 1px solid rgba(27, 107, 111, 0.25);
            background: rgba(27, 107, 111, 0.07);
            color: #0f4f52;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .status-chip.alert {
            border-color: rgba(179, 63, 63, 0.3);
            background: rgba(179, 63, 63, 0.1);
            color: #7e2323;
        }
        .status-chip.warn {
            border-color: rgba(240, 168, 58, 0.35);
            background: rgba(240, 168, 58, 0.15);
            color: #87580a;
        }
        .result-card {
            border-radius: 14px;
            border: 1px solid rgba(52, 74, 93, 0.15);
            background: var(--steel-card);
            box-shadow: 0 10px 25px rgba(26, 39, 51, 0.06);
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.8rem;
            animation: fadeSlide 0.45s ease-out;
        }
        .mono-note {
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.8rem;
            color: #34516a;
        }
        @keyframes fadeSlide {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 900px) {
            .hero-title { font-size: 1.25rem; }
            .hero-panel { padding: 0.9rem 0.85rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> tuple[Any | None, str | None]:
    try:
        response = requests.request(method=method, url=url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        return None, f"Request failed: {exc}"

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = json.dumps(response.json(), indent=2)
        except ValueError:
            pass
        return None, f"HTTP {response.status_code}: {detail}"

    try:
        return response.json(), None
    except ValueError:
        return {"raw": response.text}, None


def compose_special_requirements(
    base_special: str,
    industry: str,
    finish: str,
    application_description: str,
) -> str | None:
    segments = [base_special.strip()]
    if industry.strip():
        segments.append(f"industry={industry.strip()}")
    if finish.strip():
        segments.append(f"finish={finish.strip()}")
    if application_description.strip():
        segments.append(f"application={application_description.strip()}")
    merged = "; ".join(part for part in segments if part)
    return merged or None


def render_citations(citations: list[dict[str, Any]]) -> None:
    if not citations:
        st.info("No citations returned.")
        return

    for i, citation in enumerate(citations, start=1):
        source = citation.get("source", "unknown")
        score = citation.get("score", 0.0)
        snippet = citation.get("snippet", "")
        with st.expander(f"Citation {i}: {source} (score={score:.4f})"):
            st.write(snippet)


def local_file_listing(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(str(p) for p in path.iterdir() if p.is_file())


st.set_page_config(
    page_title="Manufacturing AI Copilot",
    page_icon=":factory:",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

if "feature_editor" not in st.session_state:
    st.session_state.feature_editor = json.dumps(DEFAULT_FEATURES, indent=2)

with st.sidebar:
    st.header("Control Panel")
    api_base = st.text_input("API Base URL", value="http://localhost:8000")
    st.caption(
        "Demo URL: `http://localhost:8501` after `make run-ui`.\n"
        "API docs: `http://localhost:8000/docs`."
    )
    if st.button("Ping API Health"):
        health_payload, health_error = api_json("GET", f"{api_base}/health", timeout=15)
        if health_error:
            st.error(health_error)
        else:
            st.success("API reachable")
            st.json(health_payload)
    st.markdown("---")
    st.markdown("**Runbook**")
    st.code("make seed-data\nmake ingest-docs\nmake train-ml\nmake run-api\nmake run-ui")

st.markdown(
    """
    <div class="hero-panel">
      <div class="hero-title">Manufacturing AI Copilot</div>
      <p class="hero-sub">
        Enterprise-style local demo for quote operations and steel defect intelligence.
      </p>
      <div style="margin-top: 0.55rem;">
        <span class="status-chip">Local-First</span>
        <span class="status-chip">FastAPI + Streamlit</span>
        <span class="status-chip">Rule Engine + RAG + XGBoost</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

quote_tab, ml_tab, diag_tab = st.tabs(
    ["Quote Assistant", "Steel Defect Classifier", "Admin / Diagnostics"]
)

with quote_tab:
    st.subheader("Quote Intake + Draft Orchestration")
    c1, c2, c3 = st.columns(3)
    with c1:
        request_id = st.text_input("Request ID", value="REQ-001")
        customer_name = st.text_input("Customer Name", value="Acme Precision")
        industry = st.text_input("Industry", value="Aerospace")
        alloy_name = st.selectbox("Requested Alloy", ["316L", "304", "17-7PH"])
        product_form = st.selectbox("Product Form", ["foil", "sheet", "strip"])
    with c2:
        thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=0.04, step=0.01)
        width_mm = st.number_input("Width (mm)", min_value=0.0, value=120.0, step=5.0)
        qty_kg = st.number_input("Quantity (kg)", min_value=0.0, value=100.0, step=10.0)
        temper = st.text_input("Temper", value="Full Hard")
        finish = st.text_input("Finish", value="Bright Annealed")
    with c3:
        cert_required = st.text_input("Cert Required", value="EN_10204_3.1")
        lead_days = st.number_input("Required Lead Time (days)", min_value=1, value=14)
        application_description = st.text_area(
            "Application Description",
            value="Precision stamped shielding component.",
            height=90,
        )
        special = st.text_area("Special Requirements", value="tight tolerance", height=90)

    quote_payload = {
        "request_id": request_id,
        "customer_name": customer_name,
        "alloy_name": alloy_name,
        "product_form": product_form,
        "thickness_mm": float(thickness_mm),
        "width_mm": float(width_mm),
        "qty_kg": float(qty_kg),
        "cert_required": cert_required,
        "temper": temper,
        "required_lead_time_days": int(lead_days),
        "special_requirements": compose_special_requirements(
            base_special=special,
            industry=industry,
            finish=finish,
            application_description=application_description,
        ),
    }

    action_col_1, action_col_2 = st.columns(2)
    with action_col_1:
        if st.button("Validate Quote", use_container_width=True):
            with st.spinner("Running deterministic quote validation..."):
                payload, error = api_json(
                    "POST",
                    f"{api_base}/quote/validate",
                    payload=quote_payload,
                    timeout=40,
                )
            if error:
                st.error(error)
            else:
                st.session_state.quote_validation = payload
    with action_col_2:
        if st.button("Generate Draft Quote", use_container_width=True):
            with st.spinner("Generating quote draft from rules + retrieval..."):
                payload, error = api_json(
                    "POST",
                    f"{api_base}/quote/draft",
                    payload=quote_payload,
                    timeout=90,
                )
            if error:
                st.error(error)
            else:
                st.session_state.quote_draft = payload

    if st.session_state.get("quote_validation"):
        validation = st.session_state.quote_validation
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("##### Validation Result")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Confidence", f"{validation.get('confidence', 0.0):.3f}")
        m2.metric("Missing Fields", len(validation.get("missing_fields", [])))
        m3.metric("Warnings", len(validation.get("warnings", [])))
        m4.metric("Valid", "Yes" if validation.get("is_valid", False) else "No")
        if validation.get("escalation_required"):
            st.markdown(
                '<span class="status-chip alert">Escalation Required</span>',
                unsafe_allow_html=True,
            )
        elif validation.get("warnings"):
            st.markdown(
                '<span class="status-chip warn">Review Suggested</span>', unsafe_allow_html=True
            )
        else:
            st.markdown('<span class="status-chip">Clear to Draft</span>', unsafe_allow_html=True)

        missing_fields = validation.get("missing_fields", [])
        if missing_fields:
            st.warning("Missing info: " + ", ".join(missing_fields))

        warning_rows = validation.get("warnings", [])
        if warning_rows:
            st.dataframe(pd.DataFrame(warning_rows), use_container_width=True)

        suggested = validation.get("suggested_actions", [])
        if suggested:
            st.info("Actions: " + " | ".join(suggested))
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("quote_draft"):
        draft_payload = st.session_state.quote_draft
        draft = draft_payload.get("draft", {})
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("##### Draft Result")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Escalation", "Yes" if draft_payload.get("escalation_required") else "No")
        d2.metric("Fallback Used", "Yes" if draft_payload.get("used_fallback") else "No")
        d3.metric("Citations", len(draft_payload.get("citations", [])))
        d4.metric("Similar Quotes", len(draft.get("similar_quotes", [])))

        summary = draft.get("summary", "No summary returned.")
        st.write(f"**Summary:** {summary}")
        st.write(f"**Price Hint:** {draft.get('price_hint', 'N/A')}")

        similar_quotes = draft.get("similar_quotes", [])
        if similar_quotes:
            st.markdown("**Similar Quote Matches**")
            st.dataframe(pd.DataFrame(similar_quotes), use_container_width=True)

        st.markdown("**Citations**")
        render_citations(draft_payload.get("citations", []))

        with st.expander("Raw Draft JSON"):
            st.json(draft_payload)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Ask Documentation (RAG Q&A)")
    qa_col_1, qa_col_2 = st.columns([4, 1])
    with qa_col_1:
        doc_query = st.text_input(
            "Question",
            value="What cert constraints apply to 316L foil and how do lead times change?",
        )
    with qa_col_2:
        top_k = st.slider("Top K", min_value=1, max_value=8, value=5)

    if st.button("Ask Quote Assistant", use_container_width=True):
        with st.spinner("Retrieving cited policy context..."):
            payload, error = api_json(
                "POST",
                f"{api_base}/quote/answer",
                payload={"query": doc_query, "top_k": top_k},
                timeout=70,
            )
        if error:
            st.error(error)
        else:
            st.session_state.quote_answer = payload

    if st.session_state.get("quote_answer"):
        answer_payload = st.session_state.quote_answer
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.write(answer_payload.get("answer", ""))
        render_citations(answer_payload.get("citations", []))
        st.markdown("</div>", unsafe_allow_html=True)

with ml_tab:
    st.subheader("Steel Defect Classifier")
    train_col_1, train_col_2 = st.columns([1, 2])
    with train_col_1:
        if st.button("Train / Refresh Model", use_container_width=True):
            with st.spinner("Training model and writing artifacts..."):
                payload, error = api_json(
                    "POST",
                    f"{api_base}/ml/train/steel-faults",
                    payload={},
                    timeout=600,
                )
            if error:
                st.error(error)
            else:
                st.session_state.train_payload = payload
    with train_col_2:
        train_payload = st.session_state.get("train_payload")
        if train_payload:
            macro_f1 = train_payload.get("metrics", {}).get("macro_f1", 0.0)
            st.success(f"Latest training macro F1: {macro_f1:.4f}")
            st.caption(train_payload.get("model_path", ""))

    st.markdown("#### Single Prediction and Explainability")
    preset_col, load_col = st.columns([3, 1])
    with preset_col:
        preset_name = st.selectbox("Feature Preset", list(FEATURE_PRESETS.keys()))
    with load_col:
        if st.button("Load Preset", use_container_width=True):
            st.session_state.feature_editor = json.dumps(FEATURE_PRESETS[preset_name], indent=2)

    feature_text = st.text_area(
        "Feature JSON",
        key="feature_editor",
        height=320,
    )
    infer_col_1, infer_col_2 = st.columns(2)
    with infer_col_1:
        if st.button("Predict Single", use_container_width=True):
            try:
                features = json.loads(feature_text)
            except ValueError as exc:
                st.error(f"Invalid JSON: {exc}")
                features = None
            if features is not None:
                payload, error = api_json(
                    "POST",
                    f"{api_base}/ml/predict/steel-faults",
                    payload={"features": features},
                    timeout=60,
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.single_prediction = payload
    with infer_col_2:
        if st.button("Explain Single", use_container_width=True):
            try:
                features = json.loads(feature_text)
            except ValueError as exc:
                st.error(f"Invalid JSON: {exc}")
                features = None
            if features is not None:
                payload, error = api_json(
                    "POST",
                    f"{api_base}/ml/explain/local",
                    payload={"features": features},
                    timeout=120,
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.local_explanation = payload

    prediction = st.session_state.get("single_prediction")
    if prediction:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Predicted Class", prediction.get("predicted_class", "N/A"))
        p2.metric("Confidence", f"{prediction.get('confidence', 0.0):.4f}")
        probs = prediction.get("probabilities", {})
        if probs:
            prob_df = pd.DataFrame(
                [{"fault_class": k, "probability": v} for k, v in probs.items()]
            ).set_index("fault_class")
            st.bar_chart(prob_df)
        st.markdown("</div>", unsafe_allow_html=True)

    explanation = st.session_state.get("local_explanation")
    if explanation:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.write(f"**Local Explanation for:** `{explanation.get('predicted_class', 'N/A')}`")
        st.caption(f"Base value: {explanation.get('base_value', 0.0):.5f}")
        contrib = explanation.get("feature_contributions", {})
        if contrib:
            contrib_df = pd.DataFrame(
                [{"feature": k, "contribution": v} for k, v in contrib.items()]
            ).set_index("feature")
            st.bar_chart(contrib_df)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### Batch Scoring + Drift Snapshot")
    uploaded = st.file_uploader("Upload CSV with feature columns", type=["csv"])
    threshold = st.slider("Drift Threshold (z-score)", min_value=0.3, max_value=3.0, value=1.0)

    batch_rows: list[dict[str, Any]] = []
    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)
        st.dataframe(batch_df.head(12), use_container_width=True)
        batch_rows = batch_df.to_dict(orient="records")

    batch_col_1, batch_col_2 = st.columns(2)
    with batch_col_1:
        if st.button("Score Batch", use_container_width=True):
            if not batch_rows:
                st.warning("Upload a CSV before batch scoring.")
            else:
                payload, error = api_json(
                    "POST",
                    f"{api_base}/ml/predict/steel-faults/batch",
                    payload={"rows": batch_rows},
                    timeout=120,
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.batch_predictions = payload
    with batch_col_2:
        if st.button("Compute Drift Summary", use_container_width=True):
            if not batch_rows:
                st.warning("Upload a CSV before drift analysis.")
            else:
                payload, error = api_json(
                    "POST",
                    f"{api_base}/diagnostics/drift-summary",
                    payload={"rows": batch_rows, "threshold": threshold},
                    timeout=90,
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.drift_summary = payload

    batch_predictions = st.session_state.get("batch_predictions", {})
    if batch_predictions:
        rows = batch_predictions.get("predictions", [])
        if rows:
            scored_df = pd.DataFrame(rows)
            st.markdown("**Batch Prediction Output**")
            st.dataframe(scored_df, use_container_width=True)
            class_counts = scored_df["predicted_class"].value_counts().rename("count")
            st.bar_chart(class_counts)

    drift_payload = st.session_state.get("drift_summary", {})
    if drift_payload:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.write(
            f"**Severity:** `{drift_payload.get('severity', 'unknown')}`  "
            f"| **Rows:** {drift_payload.get('rows_evaluated', 0)}  "
            f"| **Max Shift:** {drift_payload.get('max_shift', 0.0):.4f}"
        )
        shifts = drift_payload.get("feature_shift_summary", {})
        if shifts:
            top = sorted(shifts.items(), key=lambda item: item[1], reverse=True)[:10]
            shift_df = pd.DataFrame(top, columns=["feature", "z_shift"]).set_index("feature")
            st.bar_chart(shift_df)
        flags = drift_payload.get("drift_flags", [])
        if flags:
            st.warning("Drift flags: " + ", ".join(flags))
        st.markdown("</div>", unsafe_allow_html=True)

with diag_tab:
    st.subheader("Runtime and Evaluation Diagnostics")
    dcol1, dcol2, dcol3, dcol4 = st.columns(4)
    with dcol1:
        if st.button("Health", use_container_width=True):
            payload, error = api_json("GET", f"{api_base}/health", timeout=20)
            if error:
                st.error(error)
            else:
                st.session_state.health_payload = payload
    with dcol2:
        if st.button("Runtime Status", use_container_width=True):
            payload, error = api_json("GET", f"{api_base}/diagnostics/status", timeout=30)
            if error:
                st.error(error)
            else:
                st.session_state.runtime_status = payload
    with dcol3:
        if st.button("Eval Report", use_container_width=True):
            payload, error = api_json("GET", f"{api_base}/diagnostics/eval-report", timeout=30)
            if error:
                st.error(error)
            else:
                st.session_state.eval_report = payload
    with dcol4:
        if st.button("Reindex Retrieval", use_container_width=True):
            payload, error = api_json(
                "POST", f"{api_base}/retrieval/index", payload={}, timeout=180
            )
            if error:
                st.error(error)
            else:
                st.session_state.reindex_report = payload

    left, right = st.columns(2)
    with left:
        st.markdown("##### API Health")
        if st.session_state.get("health_payload"):
            st.json(st.session_state.health_payload)
        st.markdown("##### Runtime Status")
        if st.session_state.get("runtime_status"):
            st.json(st.session_state.runtime_status)
    with right:
        st.markdown("##### Evaluation Report")
        if st.session_state.get("eval_report"):
            st.json(st.session_state.eval_report)
        st.markdown("##### Reindex Result")
        if st.session_state.get("reindex_report"):
            st.json(st.session_state.reindex_report)

    st.markdown("---")
    st.markdown("#### Local Asset Snapshot")
    local_docs = local_file_listing(Path("data/raw/internal_mock_docs")) + local_file_listing(
        Path("data/raw/ulbrich_public")
    )
    prompt_files = local_file_listing(Path("prompts"))
    snapshot_col_1, snapshot_col_2 = st.columns(2)
    with snapshot_col_1:
        st.write("**Indexed Source Files**")
        if local_docs:
            st.dataframe(pd.DataFrame({"source_file": local_docs}), use_container_width=True)
        else:
            st.info("No local docs found.")
    with snapshot_col_2:
        st.write("**Prompt Files**")
        if prompt_files:
            st.dataframe(pd.DataFrame({"prompt_file": prompt_files}), use_container_width=True)
        else:
            st.info("No prompt files found.")

st.caption(
    "Run API at `http://localhost:8000` and UI at `http://localhost:8501` for the live demo."
)
