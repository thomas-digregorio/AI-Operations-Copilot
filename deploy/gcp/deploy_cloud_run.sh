#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-ulbrich-app}"
REGION="${REGION:-us-central1}"
REPO="${REPO:-ulbrich-containers}"

API_SERVICE="${API_SERVICE:-ulbrich-api}"
UI_SERVICE="${UI_SERVICE:-ulbrich-ui}"

API_SA="${API_SA:-ulbrich-run-api@${PROJECT_ID}.iam.gserviceaccount.com}"
UI_SA="${UI_SA:-ulbrich-run-ui@${PROJECT_ID}.iam.gserviceaccount.com}"

TAG="${TAG:-$(date +%Y%m%d-%H%M%S)}"
API_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/api:${TAG}"
UI_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/ui:${TAG}"

echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Tag: ${TAG}"

gcloud config set project "${PROJECT_ID}" >/dev/null

echo "Building API image: ${API_IMAGE}"
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --config=deploy/gcp/cloudbuild.api.yaml \
  --substitutions=_IMAGE="${API_IMAGE}" \
  .

echo "Deploying API service: ${API_SERVICE}"
gcloud run deploy "${API_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --service-account="${API_SA}" \
  --port=8000 \
  --cpu=2 \
  --memory=4Gi \
  --timeout=300 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="APP_ENV=cloud,LOG_LEVEL=INFO,CORS_ALLOW_ORIGINS=*,DATABASE_URL=sqlite:////tmp/app.db,DATA_DIR=/tmp/data,MODEL_DIR=/tmp/data/artifacts/models,VECTOR_DIR=/tmp/data/artifacts/vector_index,EMBEDDING_PROVIDER=local,EMBEDDING_MODEL=BAAI/bge-small-en-v1.5,LLM_PROVIDER=ollama,LLM_MODEL=llama3.1:8b,OLLAMA_BASE_URL=http://127.0.0.1:11434,USE_LLM_FALLBACK=true" \
  --image="${API_IMAGE}"

API_URL="$(gcloud run services describe "${API_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
echo "API URL: ${API_URL}"

echo "Building UI image: ${UI_IMAGE}"
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --config=deploy/gcp/cloudbuild.ui.yaml \
  --substitutions=_IMAGE="${UI_IMAGE}" \
  .

echo "Deploying UI service: ${UI_SERVICE}"
gcloud run deploy "${UI_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --service-account="${UI_SA}" \
  --port=8501 \
  --cpu=1 \
  --memory=1Gi \
  --timeout=300 \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="API_BASE_URL=${API_URL}" \
  --image="${UI_IMAGE}"

UI_URL="$(gcloud run services describe "${UI_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
echo "UI URL: ${UI_URL}"

echo "Deployment complete."
