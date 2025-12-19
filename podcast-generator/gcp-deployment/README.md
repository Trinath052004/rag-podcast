# GCP Deployment Guide for Podcast Generator

This guide provides step-by-step instructions for deploying the Podcast Generator application to Google Cloud Platform.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Steps](#deployment-steps)
- [Configuration](#configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying to GCP, ensure you have:

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed and configured
3. **Docker** installed locally
4. **Required APIs enabled**:
   - Cloud Run
   - Cloud Build
   - Artifact Registry
   - Cloud SQL (optional)
   - Memorystore (optional)

## Architecture Overview

The GCP deployment uses the following services:

- **Cloud Run**: For containerized backend and frontend services
- **Artifact Registry**: For Docker image storage
- **Memorystore**: For Redis caching (optional)
- **Cloud SQL**: For relational database (optional)
- **Cloud Storage**: For file uploads and audio files
- **Load Balancing**: For traffic distribution
- **Cloud Monitoring**: For observability

## Deployment Steps

### 1. Set Up GCP Project

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage-component.googleapis.com
```

### 2. Create Artifact Registry

```bash
# Create a Docker repository
gcloud artifacts repositories create podcast-generator \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for Podcast Generator"
```

### 3. Build and Push Docker Images

```bash
# Build and tag images
docker-compose build

# Tag and push backend
docker tag podcast-generator_backend us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/backend:latest
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/backend:latest

# Tag and push frontend
docker tag podcast-generator_frontend us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/frontend:latest
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/frontend:latest
```

### 4. Deploy Backend to Cloud Run

```bash
gcloud run deploy podcast-generator-backend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 50 \
  --timeout 300s \
  --set-env-vars "QDRANT_HOST=YOUR_QDRANT_HOST,ELEVENLABS_API_KEY=YOUR_KEY,GEMINI_API_KEY=YOUR_KEY,SECRET_KEY=YOUR_KEY" \
  --set-secrets "ELEVENLABS_API_KEY=projects/YOUR_PROJECT_ID/secrets/ELEVENLABS_API_KEY:latest,GEMINI_API_KEY=projects/YOUR_PROJECT_ID/secrets/GEMINI_API_KEY:latest,SECRET_KEY=projects/YOUR_PROJECT_ID/secrets/SECRET_KEY:latest"
```

### 5. Deploy Frontend to Cloud Run

```bash
gcloud run deploy podcast-generator-frontend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/podcast-generator/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 5 \
  --concurrency 80 \
  --set-env-vars "REACT_APP_API_BASE_URL=https://podcast-generator-backend-YOUR_PROJECT_ID.uc.r.appspot.com/api"
```

### 6. Set Up Load Balancing (Optional)

For production environments, set up a load balancer:

```bash
gcloud compute url-maps create podcast-generator-url-map \
  --default-service podcast-generator-frontend

gcloud compute target-http-proxies create podcast-generator-proxy \
  --url-map podcast-generator-url-map

gcloud compute forwarding-rules create podcast-generator-forwarding-rule \
  --target-http-proxy podcast-generator-proxy \
  --ports 80 \
  --global
```

## Configuration

### Environment Variables

Create a `.env.gcp` file:

```env
# Backend Configuration
QDRANT_HOST=your-qdrant-host
QDRANT_PORT=6333
QDRANT_COLLECTION=podcast_chunks

# API Keys (use GCP Secret Manager)
ELEVENLABS_API_KEY=your-elevenlabs-key
GEMINI_API_KEY=your-gemini-key
SECRET_KEY=your-secret-key

# Frontend Configuration
REACT_APP_API_BASE_URL=https://your-backend-url/api
```

### GCP Secret Manager

Store sensitive keys in Secret Manager:

```bash
# Create secrets
echo "your-elevenlabs-key" | gcloud secrets create ELEVENLABS_API_KEY --data-file=-
echo "your-gemini-key" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
```

## Monitoring and Logging

### Cloud Monitoring

Set up monitoring dashboards:

```bash
# Create custom metrics
gcloud alpha monitoring custom-metrics create \
  --display-name="Podcast Generation Time" \
  --metric-kind=GAUGE \
  --value-type=DOUBLE \
  --description="Time taken to generate podcasts" \
  --unit=s
```

### Cloud Logging

Configure logging filters:

```bash
# View backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=podcast-generator-backend" --limit 50

# View frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=podcast-generator-frontend" --limit 50
```

## Scaling

### Auto-scaling Configuration

Adjust scaling parameters based on your needs:

```bash
# Update backend scaling
gcloud run services update podcast-generator-backend \
  --min-instances 2 \
  --max-instances 20 \
  --concurrency 30

# Update frontend scaling
gcloud run services update podcast-generator-frontend \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 100
```

### CPU Throttling

For cost optimization:

```bash
# Set CPU throttling
gcloud run services update podcast-generator-backend \
  --cpu-throttling
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure service account has proper IAM roles
2. **Cold Starts**: Consider minimum instances for production
3. **Timeout Errors**: Increase timeout for long-running operations
4. **Memory Issues**: Monitor memory usage and adjust limits

### Debugging

```bash
# Get service details
gcloud run services describe podcast-generator-backend

# View service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=podcast-generator-backend" --limit 100 --format json

# Check service status
gcloud run services list
```

## CI/CD Setup

### Cloud Build Configuration

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/backend:$COMMIT_SHA', './backend']

  # Push backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/backend:$COMMIT_SHA']

  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/frontend:$COMMIT_SHA', './frontend']

  # Push frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/frontend:$COMMIT_SHA']

  # Deploy backend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args: ['run', 'deploy', 'podcast-generator-backend', '--image', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/backend:$COMMIT_SHA', '--region', 'us-central1', '--platform', 'managed']

  # Deploy frontend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args: ['run', 'deploy', 'podcast-generator-frontend', '--image', 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/frontend:$COMMIT_SHA', '--region', 'us-central1', '--platform', 'managed']

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/backend:$COMMIT_SHA'
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/podcast-generator/frontend:$COMMIT_SHA'
```

### Trigger Builds

```bash
# Manual trigger
gcloud builds submit --config cloudbuild.yaml

# Set up GitHub trigger
gcloud beta builds triggers create github \
  --repo-name=YOUR_REPO \
  --repo-owner=YOUR_ORG \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Cost Optimization

### Cost-Saving Tips

1. **Use Minimum Instances**: Set to 0 for development, 1-2 for production
2. **CPU Throttling**: Enable for non-critical services
3. **Autoscaling Limits**: Set reasonable maximum instances
4. **Region Selection**: Choose cost-effective regions
5. **Monitor Usage**: Set up budget alerts

### Estimated Costs

| Service | Estimated Monthly Cost |
|---------|-----------------------|
| Cloud Run (Backend) | $50-$200 |
| Cloud Run (Frontend) | $20-$100 |
| Artifact Registry | $5-$20 |
| Secret Manager | $5-$15 |
| Cloud Storage | $10-$50 |
| **Total** | **$90-$400** |

## Security Best Practices

1. **Use IAM Roles**: Principle of least privilege
2. **Secret Management**: Never hardcode secrets
3. **Network Security**: Use VPC and firewall rules
4. **HTTPS**: Enforce HTTPS for all services
5. **Regular Updates**: Keep dependencies updated

## Next Steps

1. **Set up monitoring dashboards** in Cloud Monitoring
2. **Configure alerting policies** for critical errors
3. **Implement CI/CD pipeline** for automated deployments
4. **Set up backup and recovery** procedures
5. **Plan for scaling** as user base grows
