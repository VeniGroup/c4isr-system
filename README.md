# C4ISR System

[![CI/CD Pipeline](https://github.com/DanieleNTCentral/c4isr-system/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/DanieleNTCentral/c4isr-system/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive Command, Control, Communications, Computers, Intelligence, Surveillance, and Reconnaissance system built with microservices architecture.

## 🚀 **CI/CD Status**

This project includes a complete CI/CD pipeline with:
- ✅ **Automated Testing** (Backend & Frontend)
- ✅ **Security Scanning** (CodeQL)
- ✅ **Docker Image Building**
- ✅ **Multi-Environment Deployment**
- ✅ **Quality Gates** and automated validation

**Pipeline Status**: [View Latest Run](https://github.com/DanieleNTCentral/c4isr-system/actions)

## 🎯 **Setup Status: 80% Complete**

**Final steps remaining for 100% production readiness:**
- [ ] Configure branch protection rules
- [ ] Set up deployment environments
- [ ] Add repository topics
- [ ] Test complete workflow

**Quick Setup Guide**: [QUICK_SETUP_REFERENCE.md](QUICK_SETUP_REFERENCE.md)

## System Overview

The C4ISR system provides real-time military operations management capabilities including:
- Real-time device monitoring and data collection
- Intelligence gathering and analysis
- Communication management
- Air support coordination
- Interactive battlefield mapping
- User management and authentication

## Architecture

### Microservices
- **Device Management Service**: Handles military device data collection and monitoring
- **Intelligence Service**: Processes and analyzes intelligence data
- **Communication Service**: Manages inter-service and external communications
- **Air Support Service**: Coordinates air support requests and responses
- **Map Service**: Provides geospatial data and mapping capabilities
- **User Management Service**: Handles authentication and user permissions

### Frontend
- React-based dashboard with real-time updates
- Interactive map visualization using Leaflet
- Real-time data streaming via WebSockets

### Backend
- FastAPI microservices
- Redis for caching and real-time communication
- PostgreSQL for data persistence
- WebSocket support for real-time updates

## Quick Start

1. **Prerequisites**
   - Docker and Docker Compose
   - Node.js 18+ (for frontend development)

2. **Start the System**
   ```bash
   docker-compose up -d
   ```

3. **Access Services**
   - Frontend Dashboard: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Monitoring: http://localhost:9090 (Prometheus), http://localhost:3001 (Grafana)

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## API Documentation

Each service provides its own API documentation at `/docs` endpoint when running in development mode.

## Security

- OAuth2 authentication
- Role-based access control
- API rate limiting
- Secure communication protocols

## Monitoring

- Prometheus metrics collection
- Grafana dashboards
- Distributed tracing with OpenTelemetry
- Centralized logging

## License

This project is for educational and demonstration purposes only.
