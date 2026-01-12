# Cloud Deployment Guide

This guide explains how to deploy the Wheel Strategy Stock Analyzer API to various cloud platforms.

## Table of Contents

- [Quick Start with Docker](#quick-start-with-docker)
- [Deploy to Render.com (Easiest)](#deploy-to-rendercom)
- [Deploy to Railway](#deploy-to-railway)
- [Deploy to Google Cloud Run](#deploy-to-google-cloud-run)
- [Deploy to AWS ECS](#deploy-to-aws-ecs)
- [Deploy to Azure](#deploy-to-azure)
- [API Documentation](#api-documentation)

## Quick Start with Docker

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API locally
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Docker Container

```bash
# Build the image
docker build -t wheel-analyzer:latest .

# Run the container
docker run -p 8000:8000 wheel-analyzer:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Deploy to Render.com

**Easiest option with free tier available!**

### Method 1: Blueprint Deployment

1. Fork/clone this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select the `deployment/render/render.yaml` file
6. Click "Apply" and wait for deployment

### Method 2: Manual Deployment

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `wheel-analyzer-api`
   - **Environment**: `Docker`
   - **Plan**: `Starter` or `Free`
   - **Auto-Deploy**: `Yes`
5. Click "Create Web Service"

Your API will be live at: `https://wheel-analyzer-api.onrender.com`

**Free tier limitations**: Service spins down after 15 minutes of inactivity (first request may take 30-60 seconds).

## Deploy to Railway

Railway offers $5 free credits monthly and simple GitHub integration.

### Prerequisites

```bash
# Install Railway CLI
npm i -g @railway/cli
```

### Deployment Steps

```bash
# Login to Railway
railway login

# Link to project (or create new)
railway init

# Deploy
railway up

# Get deployment URL
railway domain
```

Or use the deployment script:

```bash
./deployment/deploy.sh railway
```

## Deploy to Google Cloud Run

Google Cloud Run offers a generous free tier and auto-scaling.

### Prerequisites

- Google Cloud account
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed
- Project created on GCP

### Deployment Steps

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/wheel-analyzer
gcloud run deploy wheel-analyzer-api \
  --image gcr.io/YOUR_PROJECT_ID/wheel-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10

# Get service URL
gcloud run services describe wheel-analyzer-api --region us-central1 --format 'value(status.url)'
```

Or use the deployment script:

```bash
./deployment/deploy.sh gcp
```

### Cost Estimate

- Free tier: 2 million requests/month
- After free tier: ~$0.40 per million requests

## Deploy to AWS ECS

Deploy using AWS Elastic Container Service with Fargate.

### Prerequisites

- AWS account
- AWS CLI configured
- Docker installed

### Quick Deployment

```bash
# Set variables
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="wheel-analyzer"

# Create ECR repository
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push image
docker build -t $ECR_REPO .
docker tag $ECR_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

# Create ECS cluster
aws ecs create-cluster --cluster-name wheel-analyzer-cluster --region $AWS_REGION

# Register task definition (update task-definition.json first)
aws ecs register-task-definition \
  --cli-input-json file://deployment/aws/task-definition.json \
  --region $AWS_REGION

# Create ECS service (requires VPC and subnet configuration)
# See AWS Console for complete setup
```

### Cost Estimate

- Fargate pricing: ~$0.04 per vCPU hour + ~$0.004 per GB memory hour
- Estimated cost: ~$30/month for 1 task running 24/7

## Deploy to Azure

Deploy using Azure Container Instances.

### Prerequisites

- Azure account
- Azure CLI installed

### Deployment Steps

```bash
# Login
az login

# Create resource group
az group create --name wheel-analyzer-rg --location eastus

# Create container registry
az acr create --resource-group wheel-analyzer-rg \
  --name wheelanalyzer --sku Basic

# Login to ACR
az acr login --name wheelanalyzer

# Build and push
docker build -t wheel-analyzer .
docker tag wheel-analyzer wheelanalyzer.azurecr.io/wheel-analyzer:latest
docker push wheelanalyzer.azurecr.io/wheel-analyzer:latest

# Deploy to ACI
az container create \
  --resource-group wheel-analyzer-rg \
  --name wheel-analyzer-api \
  --image wheelanalyzer.azurecr.io/wheel-analyzer:latest \
  --dns-name-label wheel-analyzer \
  --ports 8000 \
  --cpu 1 \
  --memory 1

# Get URL
az container show --resource-group wheel-analyzer-rg \
  --name wheel-analyzer-api \
  --query ipAddress.fqdn
```

## API Documentation

Once deployed, your API will have:

- **Swagger UI**: `https://your-url.com/docs`
- **ReDoc**: `https://your-url.com/redoc`
- **OpenAPI JSON**: `https://your-url.com/openapi.json`

### Example API Calls

```bash
# Health check
curl https://your-url.com/health

# Get popular tickers
curl https://your-url.com/api/v1/popular-tickers

# Analyze a ticker
curl https://your-url.com/api/v1/analyze/AAPL?target_dte=30

# Screen stocks
curl -X POST https://your-url.com/api/v1/screen \
  -H "Content-Type: application/json" \
  -d '{"min_market_cap": 10000000000}'

# Find best candidates
curl https://your-url.com/api/v1/candidates?min_annual_return=20&max_results=10
```

## Environment Variables

Configure these environment variables based on your platform:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PYTHONUNBUFFERED` | Python buffering | `1` |

## Monitoring and Logging

### Health Checks

The API includes a health check endpoint at `/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:00:00",
  "version": "1.0.0"
}
```

### Logs

Logs are written to:
- Console (stdout/stderr)
- `logs/` directory (if persistent storage is configured)

## Security Considerations

1. **API Keys**: For production, implement API key authentication
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **CORS**: Configure CORS appropriately for your frontend
4. **HTTPS**: Always use HTTPS in production (handled by cloud platforms)
5. **Secrets**: Never commit API keys or secrets to version control

## Performance Optimization

1. **Caching**: Implement Redis caching for frequently accessed data
2. **Database**: Add PostgreSQL for historical data storage
3. **Workers**: Use background workers for long-running tasks
4. **CDN**: Use CDN for static assets if you add a frontend

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs wheel-analyzer
# or
docker-compose logs wheel-analyzer
```

### Out of Memory

Increase memory limits:
- Docker: `--memory 2g`
- Cloud platforms: Update memory in configuration

### Slow Response Times

- Check if service is cold-starting (free tiers)
- Implement caching
- Optimize data fetching logic

## Cost Comparison

| Platform | Free Tier | Estimated Monthly Cost |
|----------|-----------|----------------------|
| Render.com | 750 hours/month | $0-7 |
| Railway | $5 credit | $5-20 |
| Google Cloud Run | 2M requests | $0-10 |
| AWS ECS Fargate | No free tier | $30+ |
| Azure ACI | No free tier | $30+ |

## Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation at `/docs`
- Review application logs

## Next Steps

After deployment:
1. Test all API endpoints
2. Set up monitoring and alerts
3. Configure custom domain (optional)
4. Implement authentication (for production)
5. Add frontend application
