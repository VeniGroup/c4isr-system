#!/bin/bash

# C4ISR System Startup Script
echo "🚀 Starting C4ISR System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Show service URLs
echo ""
echo "✅ C4ISR System is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   API Gateway: http://localhost:8000"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "🔍 Monitor logs with: docker-compose logs -f [service-name]"
echo "🛑 Stop system with: docker-compose down"
echo ""
echo "⏳ Services are starting up. Please wait a few minutes for all services to be ready."
echo "   You can check the status with: docker-compose ps"
