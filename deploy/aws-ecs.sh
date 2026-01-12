#!/bin/bash

# AWS ECS Deployment Script
# This script builds and deploys the Wheel Analyzer to AWS ECS with Fargate

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
CLUSTER_NAME="${CLUSTER_NAME:-wheel-analyzer-cluster}"
SERVICE_NAME="${SERVICE_NAME:-wheel-analyzer}"
TASK_FAMILY="${TASK_FAMILY:-wheel-analyzer-task}"
ECR_REPO="${ECR_REPO:-wheel-analyzer}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"

echo "🚀 Deploying Wheel Analyzer to AWS ECS"
echo "======================================"
echo "Region: ${AWS_REGION}"
echo "Cluster: ${CLUSTER_NAME}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed"
    echo "Please install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Create ECR repository if it doesn't exist
echo "📦 Ensuring ECR repository exists..."
aws ecr describe-repositories --repository-names ${ECR_REPO} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${ECR_REPO} --region ${AWS_REGION}

# Authenticate Docker to ECR
echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t ${ECR_REPO}:latest .

# Tag and push the image
echo "📤 Pushing image to ECR..."
docker tag ${ECR_REPO}:latest ${IMAGE_URI}
docker push ${IMAGE_URI}

# Create ECS cluster if it doesn't exist
echo "🏗️  Ensuring ECS cluster exists..."
aws ecs describe-clusters --clusters ${CLUSTER_NAME} --region ${AWS_REGION} 2>/dev/null || \
    aws ecs create-cluster --cluster-name ${CLUSTER_NAME} --region ${AWS_REGION}

# Register task definition
echo "📝 Registering task definition..."
cat > task-definition.json <<EOF
{
  "family": "${TASK_FAMILY}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "${SERVICE_NAME}",
      "image": "${IMAGE_URI}",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${SERVICE_NAME}",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json --region ${AWS_REGION}
rm task-definition.json

echo ""
echo "✅ Deployment preparation complete!"
echo "======================================"
echo "Image URI: ${IMAGE_URI}"
echo ""
echo "To complete deployment, you need to:"
echo "1. Create a VPC and subnets (if not exists)"
echo "2. Create a security group allowing inbound traffic on port 8080"
echo "3. Create or update the ECS service with the task definition"
echo ""
echo "Example service creation command:"
echo "aws ecs create-service \\"
echo "  --cluster ${CLUSTER_NAME} \\"
echo "  --service-name ${SERVICE_NAME} \\"
echo "  --task-definition ${TASK_FAMILY} \\"
echo "  --desired-count 1 \\"
echo "  --launch-type FARGATE \\"
echo "  --network-configuration \"awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}\""
