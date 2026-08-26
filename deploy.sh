#!/usr/bin/env bash
# ==============================================================================
# Documa - Google Cloud Run Deployment
# Targets: Cloud Run + Vertex AI + Firestore + Cloud Storage + Eventarc
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="documa-fleet"
# Artifact Registry, not the legacy gcr.io host: new projects have no gcr.io
# repository provisioned, so pushes there fail with uploadArtifacts denied.
AR_REPO="${DOCUMA_AR_REPO:-documa}"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:latest"

# Gemini 3.x publisher models are served from the 'global' endpoint. A regional
# value here makes every model call return 404.
MODEL_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
TRIAGE_MODEL="${DOCUMA_TRIAGE_MODEL:-gemma-4-26b-a4b-it-maas}"

# Cost controls. Scaling to zero means an idle demo costs nothing, and the
# instance ceiling stops an unexpected traffic spike draining hackathon credits.
MIN_INSTANCES="${DOCUMA_MIN_INSTANCES:-0}"
MAX_INSTANCES="${DOCUMA_MAX_INSTANCES:-3}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "ERROR: set GOOGLE_CLOUD_PROJECT first, e.g." >&2
  echo "  export GOOGLE_CLOUD_PROJECT=\$(gcloud config get-value project)" >&2
  exit 1
fi

echo "======================================================================"
echo " Deploying Documa Multi-Agent Fleet to Google Cloud Run"
echo " Project : ${PROJECT_ID}"
echo " Region  : ${REGION}   (models: ${MODEL_LOCATION})"
echo " Scaling : ${MIN_INSTANCES} to ${MAX_INSTANCES} instances"
echo "======================================================================"

# 1. Enable required APIs. aiplatform is what serves Gemini and Gemma.
echo "> Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  eventarc.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Grant the runtime service account access to Vertex and Firestore.
#    Cloud Run uses its service account rather than your local credentials, so
#    without these roles the deployed service authenticates but is denied.
echo "> Granting the Cloud Run service account model and datastore access..."
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for ROLE in roles/aiplatform.user roles/datastore.user roles/storage.objectViewer; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUNTIME_SA}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null
  echo "    ${ROLE} -> ${RUNTIME_SA}"
done

# 3. Ensure the Artifact Registry repository exists, then build into it.
echo "> Ensuring Artifact Registry repository '${AR_REPO}' exists..."
gcloud artifacts repositories describe "${AR_REPO}" \
  --location="${REGION}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud artifacts repositories create "${AR_REPO}" \
  --repository-format=docker --location="${REGION}" \
  --description="Documa container images" --project="${PROJECT_ID}"

for SA in "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" "${RUNTIME_SA}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA}" --role="roles/artifactregistry.writer" \
    --condition=None --quiet >/dev/null 2>&1 || true
done

echo "> Building container image via Cloud Build..."
gcloud builds submit --tag "${IMAGE_NAME}" --project="${PROJECT_ID}"

# 4. Deploy. DOCUMA_STRICT_MODE is on so the deployed service refuses to serve
#    simulated fallbacks - anything it reports came from a real extraction.
echo "> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_NAME}" \
  --platform=managed \
  --region="${REGION}" \
  --allow-unauthenticated \
  --min-instances="${MIN_INSTANCES}" \
  --max-instances="${MAX_INSTANCES}" \
  --memory=1Gi \
  --timeout=300 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=${MODEL_LOCATION},DOCUMA_TRIAGE_MODEL=${TRIAGE_MODEL},DOCUMA_STRICT_MODE=true" \
  --project="${PROJECT_ID}"

SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')"

echo "======================================================================"
echo " Deployment complete."
echo "   ${SERVICE_URL}"
echo "   ${SERVICE_URL}/app     dashboard"
echo "   ${SERVICE_URL}/docs    documentation"
echo ""
echo " To wire up the autonomous Eventarc path:"
echo "   gsutil mb -l ${REGION} gs://documa-receipts-bucket"
echo "   gcloud eventarc triggers create documa-intake \\"
echo "     --destination-run-service=${SERVICE_NAME} \\"
echo "     --destination-run-path=/api/events/gcs \\"
echo "     --destination-run-region=${REGION} \\"
echo "     --event-filters=\"type=google.cloud.storage.object.v1.finalized\" \\"
echo "     --event-filters=\"bucket=documa-receipts-bucket\" \\"
echo "     --location=${REGION}"
echo ""
echo " After recording your demo, stop billing entirely:"
echo "   gcloud run services delete ${SERVICE_NAME} --region=${REGION}"
echo "======================================================================"
