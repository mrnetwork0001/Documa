#!/usr/bin/env bash
# ==============================================================================
# Documa — Google Cloud Run Deployment Script
# Targets: Google Cloud Run + Firestore + Cloud Storage
# ==============================================================================

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-documa-hackathon}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="documa-fleet"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "======================================================================"
echo " 👁️ Deploying Documa Multi-Agent Fleet to Google Cloud Run"
echo " Project: ${PROJECT_ID} | Region: ${REGION}"
echo "======================================================================"

# 1. Enable required GCP API Services
echo "▶ Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Build Container Image using Google Cloud Build
echo "▶ Building Docker container image via Cloud Build..."
gcloud builds submit --tag "${IMAGE_NAME}" --project="${PROJECT_ID}"

# 3. Deploy Service to Cloud Run
echo "▶ Deploying container image to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_NAME}" \
  --platform=managed \
  --region="${REGION}" \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --project="${PROJECT_ID}"

echo "======================================================================"
echo " 🎉 Deployment Complete! Documa Fleet is live on Google Cloud Run."
echo "======================================================================"
