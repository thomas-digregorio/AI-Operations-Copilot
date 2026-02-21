from __future__ import annotations

import json

import pandas as pd
import requests
import streamlit as st

API_BASE = st.sidebar.text_input("API Base URL", value="http://localhost:8000")

st.set_page_config(page_title="Manufacturing AI Copilot", layout="wide")
st.title("Manufacturing AI Copilot")

quote_tab, ml_tab, diag_tab = st.tabs(["Quote Assistant", "Steel Defect Classifier", "Admin / Diagnostics"])

with quote_tab:
    st.subheader("Quote Validation + Draft")
    request_id = st.text_input("Request ID", value="REQ-001")
    customer_name = st.text_input("Customer Name", value="Acme Precision")
    alloy_name = st.selectbox("Alloy", ["316L", "304", "17-7PH"]) 
    product_form = st.selectbox("Product Form", ["foil", "sheet", "strip"])
    thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=0.04, step=0.01)
    width_mm = st.number_input("Width (mm)", min_value=0.0, value=120.0, step=5.0)
    qty_kg = st.number_input("Quantity (kg)", min_value=0.0, value=100.0, step=10.0)
    cert_required = st.text_input("Cert Required", value="EN_10204_3.1")
    lead_days = st.number_input("Required Lead Time (days)", min_value=1, value=14)
    special = st.text_input("Special Requirements", value="tight tolerance")

    payload = {
        "request_id": request_id,
        "customer_name": customer_name,
        "alloy_name": alloy_name,
        "product_form": product_form,
        "thickness_mm": float(thickness_mm),
        "width_mm": float(width_mm),
        "qty_kg": float(qty_kg),
        "cert_required": cert_required,
        "required_lead_time_days": int(lead_days),
        "special_requirements": special,
    }

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Validate Quote"):
            resp = requests.post(f"{API_BASE}/quote/validate", json=payload, timeout=30)
            st.json(resp.json())

    with c2:
        if st.button("Generate Draft"):
            resp = requests.post(f"{API_BASE}/quote/draft", json=payload, timeout=60)
            st.json(resp.json())

    st.subheader("Doc Q&A")
    q = st.text_input("Ask documentation question", value="What cert constraints apply to 316L foil?")
    if st.button("Ask Quote Assistant"):
        resp = requests.post(f"{API_BASE}/quote/answer", json={"query": q, "top_k": 5}, timeout=60)
        st.json(resp.json())

with ml_tab:
    st.subheader("Steel Fault Model")

    if st.button("Train Model"):
        resp = requests.post(f"{API_BASE}/ml/train/steel-faults", json={}, timeout=600)
        st.json(resp.json())

    sample_features_text = st.text_area(
        "Single Prediction Features (JSON)",
        value=json.dumps(
            {
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
            },
            indent=2,
        ),
        height=280,
    )

    if st.button("Predict Single"):
        features = json.loads(sample_features_text)
        resp = requests.post(
            f"{API_BASE}/ml/predict/steel-faults",
            json={"features": features},
            timeout=60,
        )
        st.json(resp.json())

    if st.button("Explain Single"):
        features = json.loads(sample_features_text)
        resp = requests.post(
            f"{API_BASE}/ml/explain/local",
            json={"features": features},
            timeout=120,
        )
        st.json(resp.json())

with diag_tab:
    st.subheader("Runtime Diagnostics")
    if st.button("Get Diagnostics Status"):
        resp = requests.get(f"{API_BASE}/diagnostics/status", timeout=30)
        st.json(resp.json())

    st.subheader("Drift Summary")
    rows_text = st.text_area(
        "Batch Rows JSON",
        value=json.dumps([json.loads(sample_features_text)], indent=2),
        height=180,
    )
    if st.button("Compute Drift"):
        rows = json.loads(rows_text)
        resp = requests.post(
            f"{API_BASE}/diagnostics/drift-summary",
            json={"rows": rows},
            timeout=60,
        )
        st.json(resp.json())

st.caption("Local-first demo UI. Ensure FastAPI service is running before using this page.")
