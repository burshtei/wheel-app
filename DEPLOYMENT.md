# Deployment Guide

This guide explains how to deploy the Wheel Strategy Stock Analyzer to various cloud platforms.

## Overview

The application is containerized using Docker and can be deployed to:
- Google Cloud Run (easiest, recommended)
- AWS ECS with Fargate
- Azure Container Instances
- Any Kubernetes cluster

## Prerequisites

- Docker installed locally
- Cloud provider CLI tools (gcloud, aws, or az)
- Active cloud provider account

## Quick Start with Docker

### Run locally with Docker:

```bash
# Build the image
docker build -t wheel-analyzer .

# Run the container
docker run -p 8080:8080 wheel-analyzer

# Test the API
curl http://localhost:8080/health
```

### Run with Docker Compose:

```bash
docker-compose up
```

## Cloud Deployments

### 1. Google Cloud Run (Recommended)

**Prerequisites:**
- Google Cloud account with billing enabled
- gcloud CLI installed and configured

**Steps:**

1. Set your project ID:
```bash
export GCP_PROJECT_ID="your-project-id"
```

2. Run the deployment script:
```bash
chmod +x deploy/cloud-run.sh
./deploy/cloud-run.sh
```

**Or manually:**

```bash
# Build and push
gcloud builds submit --tag gcr.io/your-project-id/wheel-analyzer

# Deploy
gcloud run deploy wheel-analyzer \
  --image gcr.io/your-project-id/wheel-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

**Cost:** ~$0.024/hour when active (with generous free tier)

### 2. AWS ECS with Fargate

**Prerequisites:**
- AWS account
- AWS CLI installed and configured

**Steps:**

1. Configure AWS region:
```bash
export AWS_REGION="us-east-1"
```

2. Run the deployment script:
```bash
chmod +x deploy/aws-ecs.sh
./deploy/aws-ecs.sh
```

3. Complete the service creation (see script output for instructions)

**Cost:** ~$0.04/hour per task

### 3. Azure Container Instances

**Prerequisites:**
- Azure account
- Azure CLI installed

**Steps:**

1. Run the deployment script:
```bash
chmod +x deploy/azure.sh
./deploy/azure.sh
```

**Cost:** ~$0.04/hour

### 4. Kubernetes (Any Cloud or On-Premise)

**Prerequisites:**
- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured

**Steps:**

1. Build and push your image to a container registry

2. Update the image in `deploy/kubernetes.yaml`:
```yaml
image: your-registry/wheel-analyzer:latest
```

3. Deploy:
```bash
kubectl apply -f deploy/kubernetes.yaml
```

4. Get the service URL:
```bash
kubectl get service wheel-analyzer -n wheel-analyzer
```

## API Endpoints

Once deployed, your API will be available at the following endpoints:

- `GET /` - API information
- `GET /health` - Health check
- `POST /screen` - Screen stocks for wheel strategy
- `GET /analyze/{ticker}` - Analyze specific ticker
- `POST /compare` - Compare multiple tickers
- `POST /best-candidates` - Find best wheel candidates
- `GET /ticker/{ticker}/puts` - Get put opportunities
- `GET /ticker/{ticker}/calls` - Get call opportunities

## Example API Usage

```bash
# Health check
curl https://your-app-url/health

# Analyze Apple stock
curl https://your-app-url/analyze/AAPL

# Screen stocks
curl -X POST https://your-app-url/screen \
  -H "Content-Type: application/json" \
  -d '{
    "min_market_cap": 10000000000,
    "min_iv_rank": 30,
    "min_options_volume": 1000
  }'

# Get put opportunities for Tesla
curl "https://your-app-url/ticker/TSLA/puts?target_dte=30"

# Compare opportunities
curl -X POST https://your-app-url/compare \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "strategy": "put"
  }'
```

## Monitoring and Logs

### Google Cloud Run:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=wheel-analyzer" --limit 50
```

### AWS ECS:
```bash
aws logs tail /ecs/wheel-analyzer --follow
```

### Azure:
```bash
az container logs --resource-group wheel-analyzer-rg --name wheel-analyzer --follow
```

### Kubernetes:
```bash
kubectl logs -f deployment/wheel-analyzer -n wheel-analyzer
```

## Environment Variables

You can configure the following environment variables:

- `PYTHONUNBUFFERED`: Set to "1" for real-time logging (default: 1)
- Add your API keys for premium data sources in the config

## Scaling

### Google Cloud Run:
- Auto-scales from 0 to configured max instances
- Configure with `--max-instances` flag

### AWS ECS:
- Configure desired task count in service
- Use Application Auto Scaling for dynamic scaling

### Azure Container Instances:
- Manual scaling by updating container count
- Consider using Azure Container Apps for auto-scaling

### Kubernetes:
- HorizontalPodAutoscaler included in kubernetes.yaml
- Scales from 2 to 10 replicas based on CPU/memory

## Cost Optimization

1. **Google Cloud Run**: Best for sporadic usage, pay only when active
2. **AWS Fargate**: Consider Spot instances for non-critical workloads
3. **Azure**: Use ACI for simple deployments, AKS for production
4. **All platforms**: Set appropriate memory/CPU limits to avoid over-provisioning

## Security Considerations

1. **Authentication**: Add API authentication for production use
2. **HTTPS**: All cloud platforms provide HTTPS by default
3. **Rate Limiting**: Consider adding rate limiting middleware
4. **API Keys**: Store data provider API keys in secrets manager:
   - Google Cloud: Secret Manager
   - AWS: Secrets Manager or Parameter Store
   - Azure: Key Vault

## Troubleshooting

### Container won't start:
- Check logs for dependency installation issues
- Verify all required files are in the Docker image
- Check memory/CPU limits

### API returns errors:
- Verify external API access (yfinance, etc.)
- Check network policies/firewall rules
- Review application logs

### Slow response times:
- Increase memory/CPU allocation
- Consider caching frequently requested data
- Use a CDN for static content

## Next Steps

1. Add API authentication (OAuth2, API keys)
2. Implement caching (Redis, Memcached)
3. Add monitoring (Prometheus, DataDog, CloudWatch)
4. Set up CI/CD pipeline
5. Configure custom domain
6. Add rate limiting and quotas

## Support

For issues or questions:
- Check application logs
- Review this documentation
- Open an issue on GitHub
