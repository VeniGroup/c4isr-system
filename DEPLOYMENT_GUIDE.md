# 🚀 C4ISR System Deployment Guide

## 🎯 Overview

This guide covers the complete deployment of the C4ISR system using CI/CD pipelines, from local development to production environments.

## 🔄 CI/CD Pipeline Architecture

### Pipeline Stages

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Push     │───▶│   Automated     │───▶│   Security      │───▶│   Build &       │
│                 │    │   Testing       │    │   Scanning      │    │   Deploy        │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Workflow Triggers

- **Push to `develop`**: Triggers testing + staging deployment
- **Push to `main`**: Triggers full pipeline + production deployment
- **Pull Request**: Triggers testing + security scanning

## 🛠️ Local Development Setup

### Prerequisites

```bash
# Required software
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Git

# Verify installations
docker --version
docker-compose --version
node --version
python --version
git --version
```

### Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd c4isr-system

# Start all services
chmod +x start.sh
./start.sh

# Access services
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
# Monitoring: http://localhost:9090 (Prometheus), http://localhost:3001 (Grafana)
```

## 🔧 CI/CD Pipeline Configuration

### GitHub Actions Workflow

The CI/CD pipeline is defined in `.github/workflows/ci-cd.yml` and includes:

#### 1. **Testing Stage**
```yaml
test-backend:
  - Python 3.11 setup
  - System dependencies installation
  - Python package installation
  - Automated testing

test-frontend:
  - Node.js 18 setup
  - NPM dependencies
  - Test execution
  - Build verification
```

#### 2. **Security Stage**
```yaml
security-scan:
  - CodeQL analysis
  - Vulnerability detection
  - Security best practices
  - Dependency scanning
```

#### 3. **Build Stage**
```yaml
docker-build:
  - Backend image build
  - Frontend image build
  - Docker Hub push (if configured)
  - Image caching
```

#### 4. **Deployment Stage**
```yaml
deploy-staging:    # develop branch
deploy-production: # main branch
```

### Pipeline Configuration

#### Environment Variables

Set these in GitHub Secrets:

```bash
# Docker Hub (optional)
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_access_token

# Database (for deployment)
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port

# API Keys
JWT_SECRET_KEY=your-secret-key
```

#### Branch Protection Rules

Configure in GitHub repository settings:

```yaml
main branch:
  - Require pull request reviews
  - Require status checks to pass
  - Require branches to be up to date
  - Include administrators

develop branch:
  - Require pull request reviews
  - Require status checks to pass
```

## 🚀 Deployment Environments

### 1. **Development Environment**

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  # Development overrides
  backend:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
```

### 2. **Staging Environment**

```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  # Staging configuration
  backend:
    environment:
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
```

### 3. **Production Environment**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  # Production configuration
  backend:
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
```

## 🔐 Security Configuration

### Authentication & Authorization

```python
# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Role-based Access Control
ROLES = {
    "admin": ["all"],
    "commander": ["command", "intelligence", "operations"],
    "intelligence": ["intelligence", "analysis"],
    "operator": ["operations", "devices"]
}
```

### API Security

```yaml
# Kong API Gateway Security
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
  
  - name: cors
    config:
      origins: ["https://yourdomain.com"]
      credentials: true
```

## 📊 Monitoring & Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: 'c4isr-services'
    static_configs:
      - targets: ['device-service:8002', 'intelligence-service:8003']
    metrics_path: /metrics
    scrape_interval: 15s
```

### Grafana Dashboards

Pre-configured dashboards for:
- Service health monitoring
- API performance metrics
- Database performance
- System resource usage

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": check_db_health(),
            "redis": check_redis_health(),
            "external_apis": check_external_apis()
        }
    }
```

## 🔄 Deployment Process

### Automated Deployment Flow

```mermaid
graph TD
    A[Code Push] --> B[Automated Tests]
    B --> C[Security Scan]
    C --> D[Build Images]
    D --> E[Deploy to Staging]
    E --> F[Integration Tests]
    F --> G[Deploy to Production]
    G --> H[Health Checks]
    H --> I[Monitoring Setup]
```

### Manual Deployment Commands

```bash
# Deploy specific service
docker-compose up -d device-service

# Scale services
docker-compose up -d --scale device-service=3

# Rolling update
docker-compose pull device-service
docker-compose up -d device-service

# Health check
curl http://localhost:8002/health
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Service Won't Start**
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Verify configuration
docker-compose config
```

#### 2. **Database Connection Issues**
```bash
# Check database status
docker-compose exec postgres pg_isready

# Verify environment variables
docker-compose exec service-name env | grep DATABASE
```

#### 3. **Network Issues**
```bash
# Check network connectivity
docker network ls
docker network inspect c4isr_c4isr-network

# Test inter-service communication
docker-compose exec service-name ping other-service
```

### Debug Commands

```bash
# Interactive debugging
docker-compose exec service-name bash

# Real-time logs
docker-compose logs -f service-name

# Resource monitoring
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 📈 Performance Optimization

### Backend Optimization

```python
# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Redis caching
@cache(expire=300)  # 5 minutes
async def get_device_locations():
    # Implementation
```

### Frontend Optimization

```javascript
// React Query for data caching
const { data, isLoading } = useQuery('devices', fetchDevices, {
  staleTime: 30000,  // 30 seconds
  cacheTime: 300000, // 5 minutes
});

// WebSocket connection management
useEffect(() => {
  const ws = new WebSocket(WS_URL);
  ws.onmessage = (event) => {
    // Handle real-time updates
  };
  return () => ws.close();
}, []);
```

## 🔄 Rollback Procedures

### Automatic Rollback

```yaml
# Health check failure triggers rollback
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Manual Rollback

```bash
# Rollback to previous version
git checkout HEAD~1
docker-compose down
docker-compose up -d

# Or rollback specific service
docker-compose pull service-name:previous-tag
docker-compose up -d service-name
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Monitoring Tools
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [Kong](https://docs.konghq.com/)

### Security Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Security Headers](https://securityheaders.com/)

---

**Note**: This deployment guide provides a production-ready setup. Customize configurations based on your specific infrastructure and requirements.
