#!/bin/bash

# Google Cloud Run Deployment Script
# This script builds and deploys the Wheel Analyzer to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
SERVICE_NAME="${SERVICE_NAME:-wheel-analyzer}"
REGION="${REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Wheel Analyzer to Google Cloud Run"
echo "================================================"
echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate with Google Cloud (if needed)
echo "🔐 Checking authentication..."
gcloud auth configure-docker --quiet

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Push the image to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080 \
    --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project ${PROJECT_ID})

echo ""
echo "✅ Deployment complete!"
echo "================================================"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Test the API:"
echo "  curl ${SERVICE_URL}/health"
echo "  curl ${SERVICE_URL}/analyze/AAPL"
