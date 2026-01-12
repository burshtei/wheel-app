#!/bin/bash
# Deployment script for Wheel Strategy Analyzer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if deployment target is provided
if [ -z "$1" ]; then
    print_error "Please specify a deployment target"
    echo "Usage: ./deploy.sh [local|docker|render|railway|aws|gcp|azure]"
    exit 1
fi

DEPLOY_TARGET=$1

case $DEPLOY_TARGET in
    local)
        print_info "Starting local development server..."
        pip install -r requirements.txt
        python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
        ;;

    docker)
        print_info "Building and running Docker container..."
        docker build -t wheel-analyzer:latest .
        docker run -p 8000:8000 --name wheel-analyzer wheel-analyzer:latest
        ;;

    docker-compose)
        print_info "Starting services with Docker Compose..."
        docker-compose up --build -d
        print_info "API available at http://localhost:8000"
        print_info "API docs at http://localhost:8000/docs"
        ;;

    render)
        print_info "Deploying to Render.com..."
        print_warning "Make sure you have connected your GitHub repo to Render"
        print_info "1. Go to https://dashboard.render.com"
        print_info "2. Click 'New +' and select 'Web Service'"
        print_info "3. Connect your repository"
        print_info "4. Render will auto-detect the Dockerfile"
        print_info "5. Or use the render.yaml blueprint from deployment/render/"
        ;;

    railway)
        print_info "Deploying to Railway..."
        if ! command -v railway &> /dev/null; then
            print_error "Railway CLI not installed"
            print_info "Install: npm i -g @railway/cli"
            exit 1
        fi
        railway login
        railway up
        ;;

    aws)
        print_info "Deploying to AWS ECS Fargate..."
        print_warning "Make sure you have AWS CLI configured"

        # Check if AWS CLI is installed
        if ! command -v aws &> /dev/null; then
            print_error "AWS CLI not installed"
            exit 1
        fi

        print_info "Steps to deploy:"
        print_info "1. Build and push Docker image to ECR"
        print_info "2. Create ECS cluster and task definition"
        print_info "3. Create ECS service"
        print_info ""
        print_info "See deployment/aws/README.md for detailed instructions"
        ;;

    gcp)
        print_info "Deploying to Google Cloud Run..."

        if ! command -v gcloud &> /dev/null; then
            print_error "Google Cloud SDK not installed"
            exit 1
        fi

        print_info "Building and deploying to Cloud Run..."
        gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/wheel-analyzer
        gcloud run deploy wheel-analyzer-api \
            --image gcr.io/$(gcloud config get-value project)/wheel-analyzer \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
        ;;

    azure)
        print_info "Deploying to Azure Container Instances..."

        if ! command -v az &> /dev/null; then
            print_error "Azure CLI not installed"
            exit 1
        fi

        print_info "See deployment/azure/README.md for instructions"
        ;;

    *)
        print_error "Unknown deployment target: $DEPLOY_TARGET"
        echo "Available targets: local, docker, docker-compose, render, railway, aws, gcp, azure"
        exit 1
        ;;
esac

print_info "Deployment process completed!"
