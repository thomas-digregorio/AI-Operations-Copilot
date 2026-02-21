You are building a production-style AI engineering demo project in an existing GitHub repository.



Repository:

\- GitHub repo already exists and can be connected/used: https://github.com/thomas-digregorio/AI-Operations-Copilot



Project Name:

\- Manufacturing AI Copilot

\- This is an AI Engineer portfolio demo for a manufacturing company (steel/specialty metals context)



Primary Objective:

Build a local-first, production-oriented demo platform that showcases:

1\) A Quote Assistant (RAG + deterministic rule engine + structured quote draft generation)

2\) A Steel Defect Risk / Fault Classifier (ML + explainability + scoring API)



This should look like an internal enterprise tool, not a notebook demo.



==================================================

1\) PRODUCT GOAL

==================================================



Build a demo platform that demonstrates practical AI engineering for manufacturing workflows, with clear business value and production-minded design.



Business outcomes to demonstrate:

\- Quote workflow acceleration for sales / inside sales / engineering support

\- Spec retrieval with citations from public product docs

\- Deterministic rule-based validation for quote completeness and constraints

\- Quality defect prediction for manufacturing / QA workflows

\- API-first architecture that can integrate into internal systems later

\- Documentation + auditability of AI decisions, rules, and assumptions



This is a portfolio-quality project and should be built like a real internal tool.



==================================================

2\) SCOPE

==================================================



IN SCOPE (MVP+):

A) Quote Assistant Module

\- Ingest public Ulbrich docs/pages and local public files (HTML/PDF/TXT)

\- Ingest synthetic internal quoting policy docs

\- Ingest synthetic quote history CSV

\- Build RAG retrieval with citations

\- Build deterministic rule engine for quoting constraints

\- Expose:

&nbsp; - chat-style Q\&A over docs with citations

&nbsp; - structured quote draft generation (JSON)

&nbsp; - missing-info checklist

&nbsp; - confidence and escalation flags

&nbsp; - similar historical quotes lookup



B) Steel Defect Classifier Module

\- Ingest UCI Steel Plates Faults dataset (local files under data/raw/steel\_plates\_faults/)

\- Train multiclass classifier (7 classes)

\- Save model + metrics artifacts

\- Expose scoring endpoints (single + batch)

\- Expose explainability (SHAP preferred)

\- Add lightweight monitoring/drift summary



C) Shared Platform Features

\- FastAPI backend

\- Streamlit frontend

\- Database-backed app metadata and logs (Postgres preferred, SQLite acceptable fallback)

\- Dockerized local dev

\- Config-driven environment

\- Logging + tests

\- Clear docs (system design, decision log, data governance, API contracts, demo script)



OUT OF SCOPE (for now):

\- Real ERP/CRM integration

\- Enterprise SSO

\- Real internal company data

\- Fine-tuning models

\- Complex distributed deployment / Kubernetes

\- Full enterprise MLOps stack



==================================================

3\) HIGH-LEVEL ARCHITECTURE

==================================================



Build the app with clear modular boundaries:



1\. Frontend UI (Streamlit)

\- Quote Assistant page

\- Steel Defect Classifier page

\- Admin/Diagnostics page



2\. FastAPI API Layer

\- health

\- quote APIs

\- retrieval APIs

\- rules APIs

\- ML training/inference APIs

\- diagnostics APIs



3\. RAG Services

\- document ingestion/parsing

\- chunking

\- embeddings

\- vector index

\- retrieval

\- citation mapping



4\. Rule Engine

\- deterministic quote constraints

\- missing field detection

\- assumption generation

\- engineering escalation logic



5\. ML Service

\- training pipeline

\- model artifact persistence

\- inference

\- explainability

\- monitoring summaries



6\. Data Layer

\- relational DB for metadata/logs/history

\- vector store for doc retrieval (FAISS preferred for local-first; pgvector optional for later)

\- local filesystem for artifacts



7\. Observability

\- app logs

\- request logs

\- eval outputs

\- model metrics



==================================================

4\) TECH STACK (RECOMMENDED)

==================================================



Backend:

\- Python 3.11+

\- FastAPI

\- Uvicorn

\- Pydantic v2

\- SQLAlchemy

\- Alembic



RAG:

\- Choose ONE: LangChain or LlamaIndex (keep simple)

\- Embeddings provider:

&nbsp; - default to local embeddings via SentenceTransformers (free, offline-capable)

&nbsp; - support optional OpenAI embeddings only as a non-default extension

\- Vector store:

&nbsp; - Preferred: FAISS (local filesystem index)

&nbsp; - Optional alternative: pgvector (Postgres) for production migration

\- LLM provider:

&nbsp; - Preferred local runtime: Ollama

&nbsp; - Preferred model family: Llama (for example `llama3.1:8b-instruct`)

&nbsp; - keep deterministic fallback path when local LLM is unavailable

\- Parsing:

&nbsp; - pypdf

&nbsp; - beautifulsoup4

&nbsp; - trafilatura (optional)

&nbsp; - markdown/txt readers

\- Citation mapping utility



ML:

\- pandas

\- numpy

\- scikit-learn

\- xgboost (recommended final model)

\- shap

\- joblib

\- matplotlib for charts/plots generated in scripts if needed

\- mlflow optional (nice-to-have)



Frontend:

\- Streamlit



Infra:

\- Docker / docker-compose

\- Makefile

\- pytest

\- pytest-cov (optional)



==================================================

5\) REPO STRUCTURE (CREATE THIS EXACTLY, OR VERY CLOSE)

==================================================



Create the following structure (adapt if repo already has files, but preserve organization):



manufacturing-ai-copilot/

├─ README.md

├─ .env.example

├─ docker-compose.yml

├─ Makefile

├─ requirements.txt

├─ pyproject.toml

├─ docs/

│  ├─ system\_design.md

│  ├─ decision\_log.md

│  ├─ data\_governance.md

│  ├─ api\_contracts.md

│  └─ demo\_script.md

├─ app/

│  ├─ main.py

│  ├─ core/

│  │  ├─ config.py

│  │  ├─ logging.py

│  │  └─ constants.py

│  ├─ api/

│  │  ├─ routers/

│  │  │  ├─ health.py

│  │  │  ├─ quote.py

│  │  │  ├─ retrieval.py

│  │  │  ├─ rules.py

│  │  │  ├─ ml\_inference.py

│  │  │  ├─ ml\_training.py

│  │  │  └─ diagnostics.py

│  ├─ schemas/

│  │  ├─ quote.py

│  │  ├─ retrieval.py

│  │  ├─ rules.py

│  │  ├─ ml.py

│  │  └─ common.py

│  ├─ services/

│  │  ├─ quote\_assistant\_service.py

│  │  ├─ rag\_service.py

│  │  ├─ rule\_engine\_service.py

│  │  ├─ quote\_history\_service.py

│  │  ├─ steel\_model\_service.py

│  │  ├─ explainability\_service.py

│  │  └─ monitoring\_service.py

│  ├─ db/

│  │  ├─ session.py

│  │  ├─ models.py

│  │  ├─ crud/

│  │  │  ├─ quotes.py

│  │  │  ├─ docs.py

│  │  │  ├─ requests.py

│  │  │  └─ predictions.py

│  │  └─ migrations/

│  ├─ pipelines/

│  │  ├─ ingest\_ulbrich\_public\_docs.py

│  │  ├─ build\_synthetic\_quote\_data.py

│  │  ├─ ingest\_internal\_mock\_docs.py

│  │  ├─ build\_vector\_index.py

│  │  ├─ train\_steel\_fault\_model.py

│  │  ├─ evaluate\_steel\_fault\_model.py

│  │  └─ generate\_business\_enriched\_steel\_data.py

│  └─ utils/

│     ├─ text\_chunking.py

│     ├─ citation\_utils.py

│     ├─ file\_loaders.py

│     ├─ metrics.py

│     └─ seed.py

├─ frontend/

│  └─ streamlit\_app.py

├─ data/

│  ├─ raw/

│  │  ├─ ulbrich\_public/

│  │  ├─ steel\_plates\_faults/

│  │  └─ internal\_mock\_docs/

│  ├─ processed/

│  │  ├─ rag\_chunks/

│  │  ├─ quote\_history\_synthetic.csv

│  │  ├─ pricing\_rules.csv

│  │  ├─ material\_catalog.csv

│  │  └─ steel\_faults\_processed.csv

│  ├─ business\_enriched/

│  │  └─ steel\_faults\_enriched.csv

│  └─ artifacts/

│     ├─ vector\_index/

│     ├─ models/

│     ├─ metrics/

│     └─ evals/

├─ prompts/

│  ├─ quote\_assistant\_system.txt

│  ├─ quote\_draft\_generation.txt

│  ├─ quote\_missing\_info\_check.txt

│  └─ retrieval\_answering.txt

└─ tests/

&nbsp;  ├─ test\_quote\_rules.py

&nbsp;  ├─ test\_quote\_api.py

&nbsp;  ├─ test\_rag\_retrieval.py

&nbsp;  ├─ test\_ml\_training.py

&nbsp;  ├─ test\_ml\_inference.py

&nbsp;  └─ test\_schemas.py



If the repo root is already AI-Operations-Copilot, put these files/folders in that repo root (do not nest another unnecessary top-level folder unless needed).



==================================================

6\) DATA DESIGN

==================================================



6.1 Quote Assistant Data Sources



A) Public Ulbrich content (source corpus)

\- The user wants to use Ulbrich public content as the external/public corpus.

\- Ingest from local files placed under:

&nbsp; - data/raw/ulbrich\_public/

\- Support HTML, PDF, TXT, MD

\- If no files exist, create placeholder ingestion logic and clear README instructions on how to populate this folder manually.



B) Synthetic internal mock docs (must generate)

Create 6–10 realistic internal mock quoting docs (Markdown or text/PDF-like content) in:

\- data/raw/internal\_mock\_docs/



Create at least:

\- Sales\_Quote\_SOP\_v1.md

\- Lead\_Time\_and\_MOQ\_Policy\_v1.md

\- Certifications\_and\_Compliance\_Policy.md

\- Packaging\_and\_Shipping\_Constraints.md

\- Escalation\_Rules\_for\_Engineering\_Review.md

\- Pricing\_Guidelines\_Internal\_v1.csv

\- Customer\_Quote\_Request\_Template.md



These must be clearly labeled synthetic in file headers and comments.



C) Synthetic quote history table (must generate)

Create:

\- data/processed/quote\_history\_synthetic.csv

\- 2,000–5,000 rows

\- realistic manufacturing quote fields

\- plausible ranges and relationships



D) Material catalog (must generate)

Create:

\- data/processed/material\_catalog.csv

\- normalized alloy/product support data used by rules and quote assistant



E) Pricing rules (must generate)

Create:

\- data/processed/pricing\_rules.csv

\- range-based pricing/lead-time constraints for deterministic logic



6.2 Required Quote Data Schemas



Create CSVs with at least these columns.



material\_catalog.csv (example fields)

\- material\_id

\- alloy\_name

\- alloy\_family

\- uns\_number

\- product\_forms\_supported (semicolon-delimited)

\- min\_thickness\_mm

\- max\_thickness\_mm

\- min\_width\_mm

\- max\_width\_mm

\- common\_applications

\- cert\_options (semicolon-delimited)

\- base\_lead\_time\_days

\- is\_active



pricing\_rules.csv (example fields)

\- rule\_id

\- rule\_type

\- alloy\_family

\- product\_form

\- thickness\_min\_mm

\- thickness\_max\_mm

\- qty\_min\_kg

\- qty\_max\_kg

\- price\_floor\_usd\_per\_kg

\- price\_ceiling\_usd\_per\_kg

\- lead\_time\_min\_days

\- lead\_time\_max\_days

\- requires\_eng\_review

\- notes



quote\_history\_synthetic.csv (example fields)

\- quote\_id

\- quote\_date

\- customer\_name

\- customer\_segment

\- industry

\- region

\- requested\_alloy

\- alloy\_family

\- product\_form

\- thickness\_mm

\- width\_mm

\- temper

\- finish

\- cert\_required

\- qty\_kg

\- lead\_time\_requested\_days

\- quoted\_price\_usd\_per\_kg

\- status

\- won\_lost

\- margin\_pct

\- escalated\_to\_engineering

\- notes



6.3 Quote Request API Input Schema (Pydantic)

Required/optional fields:

\- customer\_name (required)

\- industry (optional)

\- requested\_alloy (optional)

\- alloy\_family (optional)

\- product\_form (required)

\- thickness\_mm (required)

\- width\_mm (required)

\- temper (optional)

\- finish (optional)

\- cert\_required (optional)

\- qty\_kg (required)

\- lead\_time\_requested\_days (optional)

\- application\_description (optional free text)

\- special\_requirements (optional free text)



6.4 Steel Defect Classifier Data Source

Use UCI Steel Plates Faults dataset, loaded from:

\- data/raw/steel\_plates\_faults/



Requirements:

\- preserve raw file(s)

\- build processed dataset

\- build data dictionary documentation

\- convert one-hot fault labels to single multiclass target column: fault\_class

\- create processed file:

&nbsp; - data/processed/steel\_faults\_processed.csv



6.5 Business-enriched steel dataset (synthetic context layer)

Create:

\- data/business\_enriched/steel\_faults\_enriched.csv



Add synthetic columns (for realism; baseline model need not use them):

\- plant\_line\_id

\- shift

\- operator\_tenure\_months

\- alloy\_family\_context

\- order\_priority

\- inspection\_station\_id



==================================================

7\) FUNCTIONAL REQUIREMENTS

==================================================



7.1 Module A — Quote Assistant



FR-A1 Document ingestion

\- Ingest local public docs from data/raw/ulbrich\_public/

\- Ingest local internal mock docs from data/raw/internal\_mock\_docs/

\- Parse text and store metadata

\- Chunk text

\- Embed chunks

\- Build citation map

\- Persist doc/chunk metadata to DB



FR-A2 Retrieval with citations

\- POST endpoint that answers user questions using retrieved chunks

\- Return:

&nbsp; - answer text

&nbsp; - list of citations (doc\_id, title, chunk\_id, snippet)

&nbsp; - confidence score

&nbsp; - warnings if low confidence

\- If answer is not supported by retrieved docs, explicitly say so



FR-A3 Structured quote draft generation

Given quote request inputs:

\- run deterministic rules

\- retrieve relevant docs (RAG)

\- retrieve similar synthetic historical quotes

\- generate a structured quote draft JSON using LLM (or deterministic fallback if no LLM configured)

\- return:

&nbsp; - recommended alloy options (1–3)

&nbsp; - fit scores

&nbsp; - price range

&nbsp; - lead time range

&nbsp; - missing fields

&nbsp; - rule violations

&nbsp; - assumptions

&nbsp; - similar quotes

&nbsp; - citations

&nbsp; - confidence

&nbsp; - escalate\_to\_engineering



FR-A4 Rule-based validation

Implement deterministic rules for:

\- dimension support

\- product form support

\- MOQ logic

\- lead time feasibility

\- certification compatibility

\- engineering review triggers



FR-A5 Similar quote retrieval

Implement top-N similar quote search using weighted matching:

\- exact alloy match weight

\- alloy family match weight

\- product form match weight

\- thickness/width/qty closeness scoring

Return top 5 similar quotes with key fields and outcomes.



FR-A6 Auditability

Persist:

\- quote request

\- rule outputs

\- retrieved citations

\- generated draft

\- prompt version

\- model version

\- timestamp



7.2 Module B — Steel Defect Classifier



FR-B1 Training pipeline

\- Load raw UCI dataset

\- Preprocess features/labels

\- Train/val/test split (stratified)

\- Train baseline models

\- Select best by macro F1

\- Save artifact + metadata + metrics



FR-B2 Scoring API

\- Single-record scoring endpoint returns:

&nbsp; - predicted fault\_class

&nbsp; - class probabilities

&nbsp; - confidence

&nbsp; - optional local explanation



FR-B3 Batch scoring

\- CSV upload or JSON array batch scoring endpoint

\- Return predictions file or JSON plus summary stats



FR-B4 Explainability

\- Global feature importance endpoint

\- Local explanation endpoint

\- Prefer SHAP (TreeExplainer for XGBoost)

\- Fallback to model-native/permutation importance if SHAP unavailable



FR-B5 Monitoring

Track and expose:

\- prediction counts

\- class distribution

\- average confidence

\- simple drift summary vs training baseline (mean/std and optional PSI)



==================================================

8\) NON-FUNCTIONAL REQUIREMENTS

==================================================



Performance targets (local MVP):

\- Quote retrieval response < 4s (excluding remote LLM latency if external API used)

\- Rule validation < 200ms

\- Single ML prediction < 200ms

\- Batch scoring 100 rows < 5s



Reliability:

\- Structured error responses

\- Graceful validation errors

\- Idempotent ingestion/reindexing where possible



Security (demo-level but professional):

\- No hardcoded secrets

\- .env-based configuration

\- Redact sensitive fields in logs (even if synthetic)

\- Include production security notes in docs/data\_governance.md



Maintainability:

\- Typed Pydantic schemas everywhere

\- Modular services

\- Unit/integration tests

\- Versioned prompts and model metadata



==================================================

9\) API DESIGN (FASTAPI)

==================================================



Implement these routes with typed request/response schemas.



9.1 Health

GET /health

Response:

{

&nbsp; "status": "ok",

&nbsp; "service": "manufacturing-ai-copilot",

&nbsp; "version": "0.1.0"

}



9.2 Quote Assistant APIs



POST /quote/answer

Purpose: RAG Q\&A over docs with citations

Request:

{

&nbsp; "question": "What certifications are commonly available for 316L foil and what lead-time considerations apply?",

&nbsp; "top\_k": 5

}

Response includes:

\- answer

\- citations\[]

\- confidence

\- warnings\[]



POST /quote/draft

Purpose: Full quote draft generation (rules + retrieval + similar history + LLM/fallback)

Response fields include:

\- request\_id

\- recommended\_options\[]

\- missing\_fields\[]

\- rule\_violations\[]

\- assumptions\[]

\- similar\_quotes\[]

\- citations\[]

\- confidence

\- escalate\_to\_engineering



POST /quote/validate

Purpose: Rules-only validation (no LLM required)



GET /quote/history/similar

Purpose: Similar quote retrieval using structured inputs/query params or POST body



9.3 Retrieval / Ingestion APIs



POST /retrieval/ingest/public

\- ingest local files from data/raw/ulbrich\_public/



POST /retrieval/ingest/internal

\- ingest local files from data/raw/internal\_mock\_docs/



POST /retrieval/reindex

\- rebuild/recompute vector index



GET /retrieval/docs

\- list indexed docs and metadata



9.4 ML Training / Inference APIs



POST /ml/train/steel-faults

Request fields:

\- model\_type (e.g. xgboost, random\_forest, logistic\_regression)

\- use\_business\_enriched\_features (bool)

\- random\_seed



POST /ml/predict/steel-faults

\- single prediction



POST /ml/predict/steel-faults/batch

\- batch scoring



GET /ml/explain/global

\- global feature importance



POST /ml/explain/local

\- local explanation for one row



9.5 Diagnostics APIs

\- model metadata

\- last training run metrics

\- app config summary (safe fields only)

\- vector index status



==================================================

10\) DOMAIN LOGIC DESIGN

==================================================



10.1 Quote Rule Engine (deterministic, code/config)

IMPORTANT:

\- Business rules must be implemented in Python/config (NOT in prompts)

\- Use config-driven approach (YAML/CSV/JSON + evaluator)



Rule categories:

1\. Dimension support

2\. Product form support

3\. MOQ logic

4\. Lead time feasibility

5\. Certification constraints

6\. Engineering review triggers



Example engineering review triggers:

\- very thin gauge

\- unusual width/thickness combo

\- tight lead time request

\- missing critical fields

\- special requirements free text indicates custom processing



Rule output schema should include:

\- rule\_id

\- severity

\- passed

\- message

\- field\_refs



Create RuleEngineService with methods like:

\- validate(request) -> structured rule results

\- summarize(rule\_results) -> warnings/escalation



10.2 Quote Draft Generation Pipeline

Implement orchestration in this order:

1\. Validate request schema

2\. Run deterministic rule engine

3\. Retrieve relevant docs (RAG)

4\. Retrieve similar quotes

5\. Assemble structured context

6\. Generate draft JSON via LLM (strict schema), OR deterministic fallback if no LLM configured

7\. Validate output schema with Pydantic

8\. If invalid and LLM used, do one repair attempt

9\. If still invalid, return deterministic partial output + warnings

10\. Persist audit record

11\. Return response



Guardrails:

\- LLM must not invent unsupported dimensions/certs

\- Material/spec claims must map to retrieved citations or rules/material catalog

\- Price range must come from deterministic pricing rules (LLM may explain, not override)



10.3 Similar Quote Retrieval Logic

Use weighted similarity scoring:

\- exact alloy match: high weight

\- same alloy family: medium

\- same product form: medium

\- thickness closeness: numeric closeness component

\- width closeness: numeric closeness component

\- qty closeness: numeric closeness component



Return top 5 matches with:

\- quote\_id

\- comparable fields

\- quoted\_price\_usd\_per\_kg

\- won\_lost

\- margin\_pct

\- escalated\_to\_engineering



10.4 Steel Defect Model Design

\- Convert one-hot labels to single multiclass target fault\_class

\- Baseline model sequence:

&nbsp; 1) Logistic Regression

&nbsp; 2) RandomForest

&nbsp; 3) XGBoost (recommended final)

\- Evaluate with:

&nbsp; - accuracy

&nbsp; - macro F1

&nbsp; - per-class precision/recall/F1

&nbsp; - confusion matrix

&nbsp; - optional top-2 accuracy

\- Save model artifact + metadata JSON + metrics JSON

\- Expose explainability:

&nbsp; - SHAP TreeExplainer for XGBoost if available

&nbsp; - fallback method if not



==================================================

11\) UI / UX SPEC (STREAMLIT MVP)

==================================================



Create frontend/streamlit\_app.py with 3 pages/tabs:



Page 1: Quote Assistant

Sections:

1\. Quote Request Form

\- customer\_name

\- industry

\- requested\_alloy or alloy\_family

\- product\_form

\- thickness\_mm

\- width\_mm

\- temper

\- finish

\- cert\_required

\- qty\_kg

\- lead\_time\_requested\_days

\- application\_description

\- special\_requirements



2\. Generate Draft Quote

\- button + spinner



3\. Results Display

\- recommended options cards

\- price and lead-time ranges

\- missing fields checklist

\- rule warnings/errors

\- escalation badge

\- similar quotes table

\- citations accordion

\- raw JSON expander



4\. Ask Docs (RAG Q\&A)

\- text input

\- top\_k selector

\- answer + citations display



Page 2: Steel Defect Classifier

Sections:

1\. Single Prediction Form (numeric feature inputs)

2\. Batch CSV Upload

3\. Prediction Results

\- predicted class

\- class probabilities chart

\- confidence

4\. Explainability

\- local top contributing features

\- global importance chart

5\. Monitoring

\- prediction counts

\- class distribution

\- drift summary



Page 3: Admin / Diagnostics

\- indexed docs list

\- reindex button (calls API)

\- model version + metrics

\- prompt version display

\- health check

\- config summary (safe values only)



==================================================

12\) DATABASE SCHEMA (APP METADATA)

==================================================



Use SQLAlchemy models + Alembic migrations.



Required tables:

\- documents

&nbsp; - doc\_id (PK)

&nbsp; - source\_type

&nbsp; - title

&nbsp; - path\_or\_url

&nbsp; - ingested\_at

&nbsp; - checksum

&nbsp; - metadata\_json



\- document\_chunks

&nbsp; - chunk\_id (PK)

&nbsp; - doc\_id (FK)

&nbsp; - chunk\_index

&nbsp; - text

&nbsp; - embedding\_ref or embedding metadata

&nbsp; - metadata\_json



\- quote\_requests

&nbsp; - request\_id (PK)

&nbsp; - request\_json

&nbsp; - created\_at



\- quote\_drafts

&nbsp; - draft\_id (PK)

&nbsp; - request\_id (FK)

&nbsp; - response\_json

&nbsp; - rule\_results\_json

&nbsp; - citations\_json

&nbsp; - llm\_model

&nbsp; - prompt\_version

&nbsp; - created\_at



\- quote\_history

&nbsp; - ingest synthetic quote history into DB (schema mirrors CSV enough for search)



\- ml\_prediction\_logs

&nbsp; - prediction\_id (PK)

&nbsp; - model\_name

&nbsp; - model\_version

&nbsp; - input\_json

&nbsp; - output\_json

&nbsp; - created\_at



\- ml\_training\_runs

&nbsp; - run\_id (PK)

&nbsp; - model\_name

&nbsp; - params\_json

&nbsp; - metrics\_json

&nbsp; - artifact\_path

&nbsp; - created\_at



==================================================

13\) PROMPT DESIGN (LLM FILES)

==================================================



Create prompt files under prompts/:



1\) quote\_assistant\_system.txt

\- Role: manufacturing quote support copilot

\- Must use provided context/rules only

\- No unsupported claims

\- Must output structured JSON for quote drafting

\- Must surface missing information and uncertainty

\- Must include citation references passed in context



2\) quote\_draft\_generation.txt

\- Template prompt that accepts:

&nbsp; - quote request JSON

&nbsp; - rule outputs

&nbsp; - retrieved chunks

&nbsp; - similar quote summaries

&nbsp; - pricing bands

\- Outputs strict JSON



3\) quote\_missing\_info\_check.txt

\- Optional helper prompt for missing field extraction if needed

\- Can be deterministic fallback too



4\) retrieval\_answering.txt

\- For /quote/answer

\- concise answer + citations

\- admit uncertainty if not found



IMPORTANT:

\- All LLM outputs must be validated by Pydantic schemas

\- Implement one repair pass if invalid JSON

\- If still invalid, return deterministic fallback response with warnings



==================================================

14\) DATA INGESTION PIPELINES

==================================================



Implement scripts in app/pipelines/:



14.1 ingest\_ulbrich\_public\_docs.py

Goal:

\- Ingest local public docs from data/raw/ulbrich\_public/

\- Parse HTML/PDF/TXT/MD

\- Extract text and metadata

\- Chunk text

\- Save chunk artifacts / DB records



Do NOT require live crawling for MVP.

If live URL ingestion is added, make it optional.



14.2 ingest\_internal\_mock\_docs.py

\- Load internal mock docs from data/raw/internal\_mock\_docs/

\- Parse, chunk, store metadata



14.3 build\_synthetic\_quote\_data.py

Generate:

\- material\_catalog.csv

\- pricing\_rules.csv

\- quote\_history\_synthetic.csv



Requirements:

\- Use reproducible random seed

\- Use plausible manufacturing value ranges

\- Tie prices and lead times to alloy family/form/qty

\- Trigger some records with escalation flags for edge cases

\- Mark synthetic clearly (include comments/docs)



14.4 build\_vector\_index.py

\- Read parsed chunks

\- Generate embeddings (config-driven provider)

\- Build vector index

\- Persist citation mappings

\- Support reindexing



14.5 train\_steel\_fault\_model.py

\- Load raw UCI steel dataset

\- Preprocess labels/features

\- Train baseline models

\- Select best by macro F1

\- Save model/joblib + metadata + metrics



14.6 evaluate\_steel\_fault\_model.py

\- Generate confusion matrix and per-class metrics outputs

\- Save to data/artifacts/metrics/



14.7 generate\_business\_enriched\_steel\_data.py

\- Add synthetic plant context columns

\- Save enriched dataset

\- Keep baseline modeling on original features by default



==================================================

15\) MODELING DETAILS (STEEL DEFECT CLASSIFIER)

==================================================



Preprocessing:

\- Ensure numeric dtypes

\- Convert one-hot fault labels to multiclass target

\- Handle scaling for logistic regression baseline if needed

\- XGBoost can use raw numeric features



Data split:

\- 70/15/15 stratified train/val/test

\- random seed = 42 by default



Baseline sequence (must implement):

1\. LogisticRegression (multinomial or compatible multiclass)

2\. RandomForestClassifier

3\. XGBoost classifier



Model selection:

\- choose best by macro F1 on validation set

\- evaluate final on test set



Artifacts to save:

\- model .joblib

\- model\_metadata.json

\- metrics.json

\- confusion\_matrix.png

\- feature\_importance outputs

\- optional SHAP plots/serialized values



No need to force an accuracy threshold. Report honest metrics.



==================================================

16\) MONITORING / EVALUATION DESIGN

==================================================



16.1 Quote Assistant Evals

Create a JSON or YAML eval suite in:

\- data/artifacts/evals/quote\_eval\_cases.json



Add 20–30 hand-authored scenarios that test:

\- valid quote

\- missing temper

\- unsupported dimension

\- impossible lead time

\- cert mismatch

\- thin foil engineering review trigger

\- unusual special requirement



For each case store expected assertions such as:

\- expected missing fields subset

\- expected escalation boolean

\- expected rule warning presence

\- schema validity requirement



Implement a small evaluation runner script or pytest-based validation.



16.2 Steel Model Evals

Persist:

\- training/validation/test metrics

\- per-class metrics

\- confusion matrix

\- feature importance

\- example local explanations (if SHAP available)



16.3 Drift Checks (lightweight)

Implement simple drift summary for scored batches vs training baseline:

\- mean/std shifts per feature

\- optional PSI approximation

\- warning flags if thresholds exceeded



==================================================

17\) CONFIG AND ENVIRONMENT

==================================================



Create .env.example with at least:



APP\_ENV=local

LOG\_LEVEL=INFO



\# Database

DATABASE\_URL=sqlite:///./data/artifacts/app.db



\# Optional Postgres (document alternative)

\# DATABASE\_URL=postgresql+psycopg://user:pass@db:5432/manufacturing\_ai



\# RAG / Embeddings

EMBEDDING\_PROVIDER=local

EMBEDDING\_MODEL=BAAI/bge-small-en-v1.5

VECTOR\_STORE=faiss

LLM\_PROVIDER=ollama

LLM\_MODEL=llama3.1:8b-instruct

\# Local LLM runtime

OLLAMA\_BASE\_URL=http://localhost:11434

\# Optional hosted provider (non-default)

OPENAI\_API\_KEY=

\# OPENAI\_EMBEDDING\_MODEL=text-embedding-3-small

\# OPENAI\_LLM\_MODEL=gpt-4.1-mini



\# Fallback behavior (if local models are unavailable)

USE\_LLM\_FALLBACK=true



\# Paths

DATA\_DIR=./data

MODEL\_DIR=./data/artifacts/models

VECTOR\_DIR=./data/artifacts/vector\_index



Implement app/core/config.py using Pydantic Settings.



The app should run even if local LLM/embedding services are unavailable:

\- retrieval works

\- rules work

\- quote draft endpoint should return deterministic fallback with warning

\- ML pipeline works fully offline (assuming dataset files exist locally)



==================================================

18\) BUILD PLAN / IMPLEMENTATION ORDER

==================================================



Implement in phases and commit incrementally if possible.



Phase 1 — Scaffold

\- Create repo structure

\- FastAPI app with /health

\- Streamlit shell

\- Config/logging

\- Docker + Makefile

\- Basic README



Phase 2 — Quote Data + Rule Engine

\- Synthetic data generator for material catalog / pricing rules / quote history

\- Internal mock docs generator/seed files

\- Rule engine service + tests

\- /quote/validate endpoint



Phase 3 — RAG Ingestion + Retrieval

\- Ingestion pipelines for local public/internal docs

\- Chunking + embeddings + vector store

\- /quote/answer with citations

\- Retrieval tests



Phase 4 — Quote Draft Orchestration

\- Similar quote retrieval service

\- /quote/draft endpoint orchestration

\- LLM integration + fallback

\- Schema validation + repair pass

\- Audit logging



Phase 5 — Steel ML Pipeline

\- Raw dataset loader + preprocessing

\- Train/evaluate scripts

\- /ml/train/steel-faults

\- /ml/predict/steel-faults

\- /ml/predict/steel-faults/batch



Phase 6 — Explainability + UI Polish

\- SHAP global/local explainability

\- Streamlit charts and polished outputs

\- Diagnostics page



Phase 7 — Quality + Docs

\- Add/finish tests

\- Error handling cleanup

\- Complete docs files

\- Final README + demo\_script.md



==================================================

19\) TESTING REQUIREMENTS (IMPORTANT)

==================================================



You MUST run and validate your own code locally during development.



Create tests and run them:

\- unit tests

\- integration tests

\- smoke tests



Unit tests (required):

\- tests/test\_quote\_rules.py

&nbsp; - MOQ checks

&nbsp; - dimension bounds

&nbsp; - cert constraints

&nbsp; - engineering escalation triggers

\- tests/test\_schemas.py

&nbsp; - Pydantic request/response validation

\- tests/test\_ml\_training.py

&nbsp; - raw dataset load

&nbsp; - label conversion

&nbsp; - training pipeline outputs artifacts



Integration tests (required):

\- tests/test\_quote\_api.py

&nbsp; - /quote/validate

&nbsp; - /quote/draft (mock LLM or fallback mode)

\- tests/test\_rag\_retrieval.py

&nbsp; - ingestion + retrieval returns citations

\- tests/test\_ml\_inference.py

&nbsp; - scoring endpoint returns schema-valid response



Smoke tests:

\- app startup

\- DB connection

\- vector index load/init

\- model artifact load after training



Validation expectations:

\- Run formatting/linting if configured (optional but recommended)

\- Run pytest and fix failures

\- Run at least one local end-to-end smoke path:

&nbsp; - generate synthetic quote data

&nbsp; - ingest docs

&nbsp; - build vector index

&nbsp; - train steel model

&nbsp; - launch API

&nbsp; - hit health endpoint

\- If any step fails, fix code and re-run until stable



Please include a Makefile with commands like:

\- make install

\- make test

\- make run-api

\- make run-ui

\- make seed-data

\- make ingest-docs

\- make train-ml



==================================================

20\) DEMO STORYLINE SUPPORT (DOCS + UX)

==================================================



Create docs/demo\_script.md with a walkthrough for interviews.



Story 1: Quote Assistant

\- user enters a quote request for thin 316L foil with cert requirements

\- system returns recommended option(s), missing fields, lead time range, pricing range, escalation flag

\- system shows citations to source docs and rules

\- follow-up docs Q\&A demonstrates RAG retrieval



Story 2: Steel Defect Classifier

\- user enters defect feature inputs (or uploads batch CSV)

\- system returns predicted fault type and confidence

\- system shows local feature explanation

\- system shows global importance and basic monitoring



==================================================

21\) CONSTRAINTS / GUARDRAILS

==================================================



Follow these rules strictly:



1\. Keep architecture simple and modular

\- No unnecessary microservices or over-abstraction

\- Local-first runnable app



2\. Typed schemas everywhere

\- Pydantic request/response models mandatory

\- Validate all payloads



3\. Business logic belongs in code/config, not prompts

\- Quote rules must be deterministic and testable



4\. LLM outputs must be schema-validated

\- One repair attempt max

\- Fallback to deterministic partial response if invalid or unavailable



5\. Quote claims must be traceable

\- include citations and/or rule references

\- no unsupported claims



6\. Clearly label synthetic data

\- in file names, headers, docs, and README



7\. Build runnable and testable

\- provide commands

\- run tests

\- validate end-to-end flows



8\. Prefer graceful degradation

\- if local LLM runtime or embeddings are unavailable, app should still run core deterministic and ML features

\- retrieval may use local fallback or stub warning if embeddings unavailable



==================================================

22\) ADDITIONAL DELIVERABLES (MUST CREATE)

==================================================



Required files/docs:

\- README.md (setup, commands, demo steps, architecture overview)

\- docs/system\_design.md (mirror this design in project-specific detail)

\- docs/decision\_log.md (design choices and tradeoffs)

\- docs/data\_governance.md (public vs synthetic data, privacy, limitations)

\- docs/api\_contracts.md (endpoint specs)

\- docs/demo\_script.md (interview demo flow)



Also create:

\- sample synthetic internal mock docs

\- data dictionary for steel dataset columns and processed mappings

\- prompt files

\- model metadata JSON schema

\- evaluation artifacts output directories



==================================================

23\) IMPLEMENTATION NOTES / EXPECTATIONS

==================================================



\- Use clear docstrings and comments

\- Add type hints throughout

\- Prefer small, testable service functions

\- Use dependency injection patterns in FastAPI where reasonable

\- Keep Streamlit UI clean and readable

\- Make code easy to explain in an interview



If local AI services are unavailable (Ollama / local embedding model load):

\- the project should still be runnable locally

\- quote validation and rules and similar quote retrieval should work

\- quote draft endpoint should return deterministic fallback with a clear warning

\- steel ML pipeline should remain fully functional



==================================================

24\) SUCCESS CRITERIA

==================================================



The project is complete when:

\- FastAPI app runs

\- Streamlit app runs

\- Synthetic quote datasets are generated

\- Internal mock docs exist

\- Public doc ingestion pipeline works for local files

\- Vector index can be built (or degrades gracefully if embeddings unavailable)

\- /quote/validate works

\- /quote/answer works (with citations if vector index available)

\- /quote/draft works (LLM or deterministic fallback)

\- Steel model trains and saves artifacts

\- Steel prediction endpoints work

\- Explainability endpoint works

\- Tests pass

\- README and docs are complete



==================================================

25\) FINAL INSTRUCTION: RUN, TEST, VALIDATE YOUR OWN CODE

==================================================



You must not stop at writing code.

You must:

1\) run the code,

2\) run tests,

3\) fix failures,

4\) validate endpoints/workflows,

5\) ensure the repo is in a working state.



At the end, provide:

\- a concise summary of what was implemented

\- exact commands to run locally

\- any remaining limitations / TODOs

\- what was tested and what passed

