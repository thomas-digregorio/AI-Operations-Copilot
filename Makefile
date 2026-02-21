SHELL := /bin/bash
PY := ./.conda-dev/bin/python
PIP := ./.conda-dev/bin/pip
PYTEST := ./.conda-dev/bin/pytest
RUFF := ./.conda-dev/bin/ruff
UVICORN := ./.conda-dev/bin/uvicorn
STREAMLIT := ./.conda-dev/bin/streamlit

.PHONY: install lint test run-api run-ui seed-data ingest-docs train-ml smoke db-upgrade db-downgrade

install:
	$(PIP) install -r requirements.txt

lint:
	$(RUFF) check app tests

test:
	$(PYTEST)

run-api:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	$(STREAMLIT) run frontend/streamlit_app.py --server.port 8501

seed-data:
	$(PY) -m app.pipelines.build_synthetic_quote_data
	$(PY) -m app.pipelines.ingest_internal_mock_docs

ingest-docs:
	$(PY) -m app.pipelines.ingest_ulbrich_public_docs
	$(PY) -m app.pipelines.build_vector_index

train-ml:
	$(PY) -m app.pipelines.train_steel_fault_model
	$(PY) -m app.pipelines.evaluate_steel_fault_model

db-upgrade:
	$(PY) -m alembic upgrade head

db-downgrade:
	$(PY) -m alembic downgrade -1

smoke:
	$(PY) -m app.pipelines.build_synthetic_quote_data
	$(PY) -m app.pipelines.ingest_internal_mock_docs
	$(PY) -m app.pipelines.build_vector_index
	$(PY) -m app.pipelines.train_steel_fault_model
	$(PY) -m app.pipelines.evaluate_steel_fault_model
