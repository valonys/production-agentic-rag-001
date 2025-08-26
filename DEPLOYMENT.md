# Deployment Guide

This guide covers deploying the Agentic RAG system to various cloud providers and production environments.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Cloud provider account (GCP, AWS, Azure)
- API keys for LLM providers (Groq or OpenAI)

### 1. Local Development
```bash
# Clone and setup
git clone <your-repo-url>
cd production-agentic-001

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Frontend
cd ../frontend
npm install

# Run with Docker Compose
cd ..
docker-compose up
```

## ☁️ Cloud Deployment

### Google Cloud Platform (GCP)

#### Option 1: Cloud Run (Recommended)
```bash
# Build and deploy backend
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/rag-backend .
gcloud run deploy rag-backend \
  --image gcr.io/$PROJECT_ID/rag-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=$GROQ_API_KEY

# Build and deploy frontend
cd ../frontend
npm run build
gcloud builds submit --tag gcr.io/$PROJECT_ID/rag-frontend .
gcloud run deploy rag-frontend \
  --image gcr.io/$PROJECT_ID/rag-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Option 2: GKE (Kubernetes)
```bash
# Create GKE cluster
gcloud container clusters create rag-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-4

# Deploy using Kubernetes manifests
kubectl apply -f deploy/k8s/
```

### Amazon Web Services (AWS)

#### Option 1: ECS Fargate
```bash
# Create ECR repositories
aws ecr create-repository --repository-name rag-backend
aws ecr create-repository --repository-name rag-frontend

# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker build -t rag-backend -f deploy/Dockerfile.backend .
docker tag rag-backend:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest

# Deploy using AWS CLI or CloudFormation
```

#### Option 2: EKS (Kubernetes)
```bash
# Create EKS cluster
eksctl create cluster --name rag-cluster --region us-east-1 --nodes 3

# Deploy using Kubernetes manifests
kubectl apply -f deploy/k8s/
```

### Microsoft Azure

#### Option 1: Container Instances
```bash
# Create container registry
az acr create --name ragregistry --resource-group myResourceGroup --sku Basic

# Build and push images
az acr build --registry ragregistry --image rag-backend:latest .
az acr build --registry ragregistry --image rag-frontend:latest .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name rag-backend \
  --image ragregistry.azurecr.io/rag-backend:latest \
  --dns-name-label rag-backend \
  --ports 8000
```

#### Option 2: AKS (Kubernetes)
```bash
# Create AKS cluster
az aks create --resource-group myResourceGroup --name rag-cluster --node-count 3

# Deploy using Kubernetes manifests
kubectl apply -f deploy/k8s/
```

## 🔧 Environment Configuration

### Environment Variables

Create a `.env` file or set environment variables in your cloud platform:

```env
# Required: Choose one LLM provider
GROQ_API_KEY=gsk_your_groq_api_key_here
# OR
OPENAI_API_KEY=sk_your_openai_api_key_here

# LLM Configuration
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192
OPENAI_MODEL=gpt-4o-mini

# Vector Store (for persistent storage)
VECTOR_STORE_PATH=/app/data/index.faiss
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
TOP_K=5
CONTEXT_BUDGET=2000
TIMEOUT_SEC=30

# Optional: Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

### Secrets Management

#### GCP Secret Manager
```bash
# Create secrets
echo -n "your-groq-api-key" | gcloud secrets create groq-api-key --data-file=-
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-

# Reference in deployment
gcloud run deploy rag-backend \
  --set-secrets GROQ_API_KEY=groq-api-key:latest
```

#### AWS Secrets Manager
```bash
# Create secrets
aws secretsmanager create-secret --name groq-api-key --secret-string "your-groq-api-key"
aws secretsmanager create-secret --name openai-api-key --secret-string "your-openai-api-key"
```

#### Azure Key Vault
```bash
# Create key vault
az keyvault create --name rag-keyvault --resource-group myResourceGroup

# Store secrets
az keyvault secret set --vault-name rag-keyvault --name groq-api-key --value "your-groq-api-key"
az keyvault secret set --vault-name rag-keyvault --name openai-api-key --value "your-openai-api-key"
```

## 📊 Monitoring & Observability

### Health Checks
```bash
# Check API health
curl https://your-api-url/health

# Expected response
{
  "status": "healthy",
  "llm_provider": "groq",
  "version": "1.0.0"
}
```

### Logging
The application uses structured logging with correlation IDs:

```python
# Example log output
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "message": "Chat request received",
  "query": "What is the capital of France?",
  "correlation_id": "abc123"
}
```

### Metrics
Enable metrics collection by setting `ENABLE_METRICS=true`:

- Request count and latency
- Error rates
- LLM provider usage
- Vector store performance

## 🔒 Security Considerations

### Network Security
- Use HTTPS/TLS for all external communications
- Implement proper CORS policies
- Use VPC/private networks where possible
- Configure firewall rules appropriately

### Authentication & Authorization
```python
# Add authentication middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Implement your token verification logic
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
```

### Data Protection
- Encrypt data at rest and in transit
- Use managed secrets services
- Implement proper backup strategies
- Follow data retention policies

## 📈 Scaling Strategies

### Horizontal Scaling
```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-backend-hpa
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Load Balancing
- Use cloud load balancers (ALB, NLB, Cloud Load Balancer)
- Implement health checks
- Configure session affinity if needed
- Use CDN for static assets

### Database Scaling
For production use, consider:
- Managed vector databases (Pinecone, Weaviate, Qdrant)
- Distributed FAISS with Redis
- Database sharding strategies

## 🚨 Troubleshooting

### Common Issues

#### 1. API Key Errors
```bash
# Check environment variables
echo $GROQ_API_KEY
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models
```

#### 2. Memory Issues
```bash
# Monitor memory usage
kubectl top pods
docker stats

# Increase memory limits
resources:
  requests:
    memory: "2Gi"
  limits:
    memory: "4Gi"
```

#### 3. Network Connectivity
```bash
# Test internal connectivity
kubectl exec -it <pod-name> -- curl http://backend-service:8000/health

# Check DNS resolution
nslookup backend-service
```

### Debug Mode
Enable debug logging:
```env
LOG_LEVEL=DEBUG
ENABLE_DEBUG=true
```

### Performance Tuning
```env
# Optimize for performance
WORKERS=4
MAX_CONNECTIONS=1000
TIMEOUT_SEC=60
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker images
      run: |
        docker build -t rag-backend -f deploy/Dockerfile.backend .
        docker push ${{ secrets.REGISTRY }}/rag-backend:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/rag-backend \
          rag-backend=${{ secrets.REGISTRY }}/rag-backend:${{ github.sha }}
```

## 📞 Support

For deployment issues:
1. Check the logs: `kubectl logs -f deployment/rag-backend`
2. Verify configuration: `kubectl describe pod <pod-name>`
3. Test connectivity: `kubectl exec -it <pod-name> -- curl localhost:8000/health`
4. Review monitoring dashboards
5. Contact your cloud provider support

This deployment guide provides a comprehensive approach to deploying the Agentic RAG system in production environments across major cloud providers.
