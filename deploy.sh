#!/bin/bash

# C4ISR System Deployment Script
# Supports development, staging, and production environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
COMPOSE_FILES="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up $ENVIRONMENT environment..."
    
    case $ENVIRONMENT in
        "development")
            COMPOSE_FILES="$COMPOSE_FILES docker-compose.dev.yml"
            print_status "Using development configuration"
            ;;
        "staging")
            COMPOSE_FILES="$COMPOSE_FILES docker-compose.staging.yml"
            print_status "Using staging configuration"
            ;;
        "production")
            COMPOSE_FILES="$COMPOSE_FILES docker-compose.prod.yml"
            print_status "Using production configuration"
            
            # Check for production secrets
            if ! docker secret ls | grep -q "postgres_password"; then
                print_warning "Production secrets not found. Creating them..."
                echo "c4isr_production_password" | docker secret create postgres_password -
                echo "grafana_production_password" | docker secret create grafana_password -
            fi
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_status "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
    
    print_success "Environment setup completed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/prometheus
    mkdir -p data/grafana
    
    print_success "Directories created"
}

# Function to stop existing services
stop_services() {
    print_status "Stopping existing services..."
    
    docker-compose -f $COMPOSE_FILES down --remove-orphans
    
    print_success "Services stopped"
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose -f $COMPOSE_FILES build --no-cache
    
    print_success "Images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    docker-compose -f $COMPOSE_FILES up -d
    
    print_success "Services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Checking service health (attempt $attempt/$max_attempts)..."
        
        # Check if all services are running
        local running_services=$(docker-compose -f $COMPOSE_FILES ps --services --filter "status=running" | wc -l)
        local total_services=$(docker-compose -f $COMPOSE_FILES ps --services | wc -l)
        
        if [ "$running_services" -eq "$total_services" ]; then
            print_success "All services are running"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Some services may not be fully ready"
            break
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait a bit for services to fully initialize
    sleep 30
    
    # Check API Gateway
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "API Gateway is healthy"
    else
        print_warning "API Gateway health check failed"
    fi
    
    # Check Device Service
    if curl -f http://localhost:8002/health &> /dev/null; then
        print_success "Device Service is healthy"
    else
        print_warning "Device Service health check failed"
    fi
    
    # Check Frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend health check failed"
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy &> /dev/null; then
        print_success "Prometheus is healthy"
    else
        print_warning "Prometheus health check failed"
    fi
    
    # Check Grafana
    if curl -f http://localhost:3001/api/health &> /dev/null; then
        print_success "Grafana is healthy"
    else
        print_warning "Grafana health check failed"
    fi
}

# Function to show service status
show_status() {
    print_status "Service status:"
    docker-compose -f $COMPOSE_FILES ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend Dashboard: http://localhost:3000"
    echo "  API Gateway: http://localhost:8000"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001 (admin/admin)"
    
    echo ""
    print_status "Useful commands:"
    echo "  View logs: docker-compose -f $COMPOSE_FILES logs -f [service-name]"
    echo "  Stop services: docker-compose -f $COMPOSE_FILES down"
    echo "  Restart services: docker-compose -f $COMPOSE_FILES restart"
    echo "  Scale services: docker-compose -f $COMPOSE_FILES up -d --scale [service]=[count]"
}

# Function to deploy with CI/CD integration
deploy_with_cicd() {
    print_status "Deploying with CI/CD integration..."
    
    # Check if we're in a CI/CD environment
    if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
        print_status "Running in CI/CD environment"
        
        # Set environment variables from CI/CD
        export DATABASE_URL=${DATABASE_URL:-"postgresql://c4isr_user:c4isr_password@postgres:5432/c4isr"}
        export REDIS_URL=${REDIS_URL:-"redis://redis:6379"}
        export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"ci-cd-secret-key"}
        
        # Run deployment
        deploy
    else
        print_status "Running in local environment"
        deploy
    fi
}

# Main deployment function
deploy() {
    print_status "Starting deployment for $ENVIRONMENT environment..."
    
    check_prerequisites
    setup_environment
    create_directories
    stop_services
    build_images
    start_services
    wait_for_services
    check_health
    show_status
    
    print_success "Deployment completed successfully!"
}

# Function to show help
show_help() {
    echo "C4ISR System Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT]"
    echo ""
    echo "Environments:"
    echo "  development  - Development environment with debugging enabled"
    echo "  staging      - Staging environment for testing"
    echo "  production   - Production environment with optimizations"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy development environment"
    echo "  $0 development        # Deploy development environment"
    echo "  $0 staging           # Deploy staging environment"
    echo "  $0 production        # Deploy production environment"
    echo ""
    echo "Environment Variables:"
    echo "  DATABASE_URL         - PostgreSQL connection string"
    echo "  REDIS_URL           - Redis connection string"
    echo "  JWT_SECRET_KEY      - JWT secret for authentication"
    echo ""
    echo "CI/CD Integration:"
    echo "  This script automatically detects CI/CD environments and"
    echo "  configures appropriate settings for automated deployment."
}

# Main script logic
case "${1:-}" in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    "development"|"staging"|"production"|"")
        deploy_with_cicd
        ;;
    *)
        print_error "Invalid option: $1"
        show_help
        exit 1
        ;;
esac
