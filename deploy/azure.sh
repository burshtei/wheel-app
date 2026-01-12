#!/bin/bash

# Azure Container Instances Deployment Script
# This script builds and deploys the Wheel Analyzer to Azure Container Instances

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-wheel-analyzer-rg}"
CONTAINER_NAME="${CONTAINER_NAME:-wheel-analyzer}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-wheelanalyzeracr}"
IMAGE_NAME="${ACR_NAME}.azurecr.io/wheel-analyzer:latest"

echo "🚀 Deploying Wheel Analyzer to Azure Container Instances"
echo "========================================================="
echo "Resource Group: ${RESOURCE_GROUP}"
echo "Container Name: ${CONTAINER_NAME}"
echo "Location: ${LOCATION}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Error: Azure CLI is not installed"
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure (if needed)
echo "🔐 Checking Azure authentication..."
az account show &>/dev/null || az login

# Create resource group if it doesn't exist
echo "📦 Ensuring resource group exists..."
az group create --name ${RESOURCE_GROUP} --location ${LOCATION}

# Create Azure Container Registry if it doesn't exist
echo "🏗️  Ensuring Azure Container Registry exists..."
az acr show --name ${ACR_NAME} --resource-group ${RESOURCE_GROUP} 2>/dev/null || \
    az acr create --resource-group ${RESOURCE_GROUP} --name ${ACR_NAME} --sku Basic

# Enable admin access to ACR
az acr update --name ${ACR_NAME} --admin-enabled true

# Login to ACR
echo "🔐 Logging in to Azure Container Registry..."
az acr login --name ${ACR_NAME}

# Build and push the image
echo "🔨 Building and pushing Docker image..."
az acr build --registry ${ACR_NAME} --image wheel-analyzer:latest .

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name ${ACR_NAME} --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name ${ACR_NAME} --query passwords[0].value -o tsv)
ACR_SERVER="${ACR_NAME}.azurecr.io"

# Deploy to Azure Container Instances
echo "🚀 Deploying to Azure Container Instances..."
az container create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${CONTAINER_NAME} \
    --image ${IMAGE_NAME} \
    --registry-login-server ${ACR_SERVER} \
    --registry-username ${ACR_USERNAME} \
    --registry-password ${ACR_PASSWORD} \
    --dns-name-label ${CONTAINER_NAME} \
    --ports 8080 \
    --cpu 2 \
    --memory 2 \
    --restart-policy Always

# Get the FQDN
FQDN=$(az container show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${CONTAINER_NAME} \
    --query ipAddress.fqdn -o tsv)

echo ""
echo "✅ Deployment complete!"
echo "========================================================="
echo "Service URL: http://${FQDN}:8080"
echo ""
echo "Test the API:"
echo "  curl http://${FQDN}:8080/health"
echo "  curl http://${FQDN}:8080/analyze/AAPL"
