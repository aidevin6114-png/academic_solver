# Deployment Guide

This guide covers deploying the Math Problem Solver to cloud platforms.

## Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- API keys for services (OpenAI, Google Cloud Vision)

### Quick Start

1. **Clone and configure**
```bash
git clone <repository-url>
cd math-solver
cp backend/.env.example backend/.env
# Edit .env with your API keys
```

2. **Build and run**
```bash
docker-compose up --build
```

3. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## AWS Deployment

### Using AWS ECS (Elastic Container Service)

1. **Build and push Docker images**
```bash
# Build backend image
docker build -t math-solver-backend ./backend
docker tag math-solver-backend:latest <your-ecr-repo>/math-solver-backend:latest
docker push <your-ecr-repo>/math-solver-backend:latest

# Build frontend image
docker build -t math-solver-frontend ./frontend
docker tag math-solver-frontend:latest <your-ecr-repo>/math-solver-frontend:latest
docker push <your-ecr-repo>/math-solver-frontend:latest
```

2. **Create ECS task definition**
```json
{
  "family": "math-solver",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<your-ecr-repo>/math-solver-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "<your-api-key>"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/math-solver",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "frontend",
      "image": "<your-ecr-repo>/math-solver-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "links": ["backend"],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/math-solver",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Deploy using AWS CLI**
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs run-task --cluster math-solver-cluster --task-definition math-solver
```

### Using AWS EC2

1. **Launch EC2 instance**
- Choose Ubuntu 20.04 LTS
- Configure security groups (ports 80, 8000)
- Assign IAM role for S3 access

2. **Connect and deploy**
```bash
ssh ubuntu@<your-ec2-ip>
git clone <repository-url>
cd math-solver
docker-compose up -d
```

## Google Cloud Platform Deployment

### Using Google Cloud Run

1. **Build and deploy backend**
```bash
cd backend
gcloud builds submit --tag gcr.io/<project-id>/math-solver-backend
gcloud run deploy math-solver-backend \
  --image gcr.io/<project-id>/math-solver-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=<your-key>
```

2. **Build and deploy frontend**
```bash
cd frontend
gcloud builds submit --tag gcr.io/<project-id>/math-solver-frontend
gcloud run deploy math-solver-frontend \
  --image gcr.io/<project-id>/math-solver-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BACKEND_URL=<backend-service-url>
```

### Using Google Cloud Platform Services

1. **Set up Cloud Storage for file uploads**
```bash
gsutil mb gs://math-solver-uploads
gsutil iam ch allUsers:objectViewer gs://math-solver-uploads
```

2. **Configure environment variables**
```bash
export GOOGLE_CLOUD_PROJECT=<project-id>
export GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account-key>
```

## Vercel Deployment (Frontend Only)

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Deploy frontend**
```bash
cd frontend
vercel
```

3. **Configure environment variables**
- Add `VITE_API_URL` pointing to your backend

## Heroku Deployment

1. **Create Heroku apps**
```bash
heroku create math-solver-backend
heroku create math-solver-frontend
```

2. **Deploy backend**
```bash
heroku container:push web -a math-solver-backend
heroku container:release web -a math-solver-backend
heroku config:set OPENAI_API_KEY=<your-key> -a math-solver-backend
```

3. **Deploy frontend**
```bash
heroku container:push web -a math-solver-frontend
heroku container:release web -a math-solver-frontend
heroku config:set BACKEND_URL=<backend-url> -a math-solver-frontend
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `GOOGLE_CLOUD_VISION_API_KEY`: Google Cloud Vision API key for OCR

### Optional Variables
- `FRONTEND_URL`: Frontend URL for CORS configuration
- `MAX_FILE_SIZE`: Maximum file upload size (default: 10MB)
- `DATABASE_URL`: Database connection string (for production)

## Database Setup (Production)

### PostgreSQL Setup
```bash
# Using Docker
docker run -d \
  --name math-solver-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=math_solver \
  -p 5432:5432 \
  postgres:13

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/math_solver
```

### Migration Commands
```bash
cd backend
alembic upgrade head
```

## Monitoring and Logging

### AWS CloudWatch
- Enable CloudWatch logs for ECS tasks
- Set up CloudWatch dashboards for monitoring

### Google Cloud Logging
- Cloud Logging is automatically enabled for Cloud Run
- Set up log-based metrics and alerts

### Health Checks
```bash
# Backend health check
curl http://localhost:8000/api/health

# Expected response
{"status":"healthy"}
```

## SSL/TLS Configuration

### Using Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com
```

### AWS Certificate Manager
- Request certificate in ACM
- Configure load balancer to use HTTPS

## Backup and Recovery

### Database Backups
```bash
# PostgreSQL backup
pg_dump -U postgres math_solver > backup.sql

# Restore
psql -U postgres math_solver < backup.sql
```

### File Storage Backup
```bash
# Sync uploads to S3
aws s3 sync uploads/ s3://math-solver-backups/uploads/
```

## Troubleshooting

### Common Issues

1. **Container won't start**
```bash
docker logs <container-id>
docker-compose logs backend
```

2. **API connection errors**
- Check CORS configuration
- Verify environment variables
- Test API endpoints directly

3. **File upload failures**
- Check file size limits
- Verify storage permissions
- Check disk space

### Performance Optimization

1. **Enable caching**
```python
# Add Redis for caching
pip install redis
```

2. **Load balancing**
- Use AWS ALB or Google Cloud Load Balancing
- Configure health checks

3. **CDN for static assets**
- Use CloudFront or Cloud CDN
- Configure cache headers

## Security Considerations

1. **API Key Management**
- Use AWS Secrets Manager or Google Secret Manager
- Rotate keys regularly
- Never commit keys to repository

2. **Network Security**
- Configure security groups/firewall rules
- Use VPC private subnets for backend
- Enable HTTPS only

3. **Data Protection**
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement rate limiting

## Cost Optimization

1. **AWS Cost Saving**
- Use Spot instances for non-critical workloads
- Enable auto-scaling
- Use S3 lifecycle policies

2. **GCP Cost Saving**
- Use Preemptible VMs
- Set budget alerts
- Use committed use discounts

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml for scaling
services:
  backend:
    deploy:
      replicas: 3
```

### Database Scaling
- Use read replicas for PostgreSQL
- Consider managed database services (AWS RDS, Cloud SQL)

## Support

For deployment issues:
- Check application logs
- Review cloud provider documentation
- Open GitHub issue with error details