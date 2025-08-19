# C4ISR System Project Structure

## Overview
This is a comprehensive Command, Control, Communications, Computers, Intelligence, Surveillance, and Reconnaissance (C4ISR) system built with microservices architecture and modern web technologies.

## Project Structure

```
C4ISR/
├── README.md                           # Project documentation
├── PROJECT_STRUCTURE.md                # This file - project structure overview
├── docker-compose.yml                  # Docker Compose configuration
├── start.sh                           # Startup script
│
├── kong/                              # API Gateway configuration
│   └── kong.yml                      # Kong API Gateway routes and plugins
│
├── database/                          # Database initialization
│   └── init.sql                      # PostgreSQL schema and sample data
│
├── backend/                           # Backend microservices
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend service container
│   │
│   ├── shared/                       # Shared utilities and models
│   │   ├── models.py                 # Pydantic data models
│   │   ├── database.py               # Database connection and models
│   │   ├── auth.py                   # Authentication utilities
│   │   └── redis_client.py           # Redis client and utilities
│   │
│   ├── device-service/               # Device Management Service
│   │   └── main.py                   # FastAPI application (port 8002)
│   │
│   ├── intelligence-service/         # Intelligence Service
│   │   └── main.py                   # FastAPI application (port 8003)
│   │
│   ├── communication-service/        # Communication Service
│   │   └── main.py                   # FastAPI application (port 8004)
│   │
│   ├── air-support-service/          # Air Support Service
│   │   └── main.py                   # FastAPI application (port 8005)
│   │
│   ├── map-service/                  # Map Service
│   │   └── main.py                   # FastAPI application (port 8006)
│   │
│   └── user-service/                 # User Management Service
│       └── main.py                   # FastAPI application (port 8007)
│
├── frontend/                          # React frontend application
│   ├── package.json                  # Node.js dependencies
│   ├── Dockerfile                    # Frontend container
│   └── src/                          # React source code
│       ├── App.js                    # Main application component
│       ├── App.css                   # Application styles
│       ├── components/               # React components
│       │   ├── Dashboard.js          # Main dashboard
│       │   ├── Login.js              # Login component
│       │   ├── Map.js                # Interactive map
│       │   ├── DevicePanel.js        # Device management
│       │   ├── IntelligencePanel.js  # Intelligence reports
│       │   ├── AirSupportPanel.js    # Air support requests
│       │   └── CommunicationPanel.js # Communication management
│       ├── contexts/                 # React contexts
│       │   └── AuthContext.js        # Authentication context
│       ├── services/                 # API services
│       │   ├── api.js                # API client
│       │   ├── auth.js               # Authentication service
│       │   └── websocket.js          # WebSocket client
│       └── utils/                    # Utility functions
│           ├── constants.js           # Application constants
│           └── helpers.js             # Helper functions
│
└── monitoring/                        # Monitoring and observability
    ├── prometheus.yml                 # Prometheus configuration
    └── grafana/                       # Grafana dashboards and datasources
        ├── dashboards/                # Custom dashboards
        └── datasources/               # Data source configurations
```

## Services Overview

### Backend Microservices

1. **Device Management Service (Port 8002)**
   - Manages military devices (drones, sensors, radar)
   - Handles device telemetry and location updates
   - Real-time device tracking via WebSocket

2. **Intelligence Service (Port 8003)**
   - Processes intelligence reports
   - Threat level assessment
   - Intelligence data analysis

3. **Communication Service (Port 8004)**
   - Inter-service communication
   - Message routing and delivery
   - WebSocket management for real-time updates

4. **Air Support Service (Port 8005)**
   - Air support request management
   - Mission coordination
   - Aircraft assignment and tracking

5. **Map Service (Port 8006)**
   - Geospatial data management
   - Map tile serving
   - Geographic analysis

6. **User Management Service (Port 8007)**
   - User authentication and authorization
   - Role-based access control
   - User session management

### Frontend Components

1. **Dashboard**
   - Main operational view
   - Real-time data visualization
   - System status overview

2. **Interactive Map**
   - Real-time device locations
   - Battlefield situation overlay
   - Air support request visualization

3. **Device Management**
   - Device status monitoring
   - Telemetry data display
   - Device configuration

4. **Intelligence Panel**
   - Intelligence report management
   - Threat assessment tools
   - Analysis capabilities

5. **Air Support Panel**
   - Request creation and management
   - Mission status tracking
   - Aircraft coordination

6. **Communication Panel**
   - Inter-unit communication
   - Message management
   - Real-time chat

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database with PostGIS extension
- **Redis**: Caching and real-time communication
- **JWT**: Authentication and authorization
- **WebSockets**: Real-time communication

### Frontend
- **React**: User interface framework
- **Leaflet**: Interactive mapping
- **Tailwind CSS**: Styling framework
- **React Query**: Data fetching and caching
- **WebSocket**: Real-time updates

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Kong**: API Gateway
- **Prometheus**: Metrics collection
- **Grafana**: Data visualization

## Getting Started

1. **Prerequisites**
   - Docker and Docker Compose
   - Node.js 18+ (for frontend development)

2. **Quick Start**
   ```bash
   # Make startup script executable
   chmod +x start.sh
   
   # Start the entire system
   ./start.sh
   ```

3. **Access Services**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Monitoring: http://localhost:9090 (Prometheus), http://localhost:3001 (Grafana)

4. **Default Credentials**
   - Username: admin
   - Password: admin (change in production)

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn device-service.main:app --reload --port 8002
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Security Features

- JWT-based authentication
- Role-based access control
- API rate limiting
- CORS configuration
- Secure communication protocols

## Monitoring and Observability

- Prometheus metrics collection
- Grafana dashboards
- Distributed tracing with OpenTelemetry
- Centralized logging
- Health check endpoints

## Deployment

The system is designed for containerized deployment and can be easily deployed to:
- Local development environment
- Cloud platforms (AWS, Azure, GCP)
- Kubernetes clusters
- Serverless environments

## License

This project is for educational and demonstration purposes only.
