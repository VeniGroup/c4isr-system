from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime
import uuid

from shared.database import get_db, Device, DeviceTelemetry, init_db
from shared.models import (
    DeviceCreate, DeviceUpdate, DeviceResponse, DeviceTelemetryCreate, DeviceTelemetryResponse,
    BaseResponse, PaginatedResponse
)
from shared.auth import get_current_active_user, require_operator_or_higher
from shared.redis_client import (
    update_device_location, get_device_location, get_all_device_locations,
    publish_message, check_redis_health
)

# Initialize FastAPI app
app = FastAPI(
    title="C4ISR Device Management Service",
    description="Service for managing military devices and telemetry data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_health = True  # You can implement actual DB health check
    redis_health = check_redis_health()
    
    return {
        "status": "healthy" if db_health and redis_health else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "healthy" if db_health else "unhealthy",
        "redis": "healthy" if redis_health else "unhealthy"
    }

# Device endpoints
@app.post("/devices", response_model=DeviceResponse)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator_or_higher)
):
    """Create a new device"""
    try:
        # Check if device already exists
        existing_device = db.query(Device).filter(Device.device_id == device.device_id).first()
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this ID already exists"
            )
        
        # Create device location geometry
        from geoalchemy2.functions import ST_GeomFromText
        location = ST_GeomFromText(f"POINT({device.longitude} {device.latitude})", 4326)
        
        # Create new device
        db_device = Device(
            device_type=device.device_type,
            device_id=device.device_id,
            name=device.name,
            status=device.status,
            location=location,
            altitude=device.altitude,
            heading=device.heading,
            speed=device.speed,
            battery_level=device.battery_level,
            signal_strength=device.signal_strength
        )
        
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        
        # Update Redis cache
        update_device_location(
            device.device_id,
            device.latitude,
            device.longitude,
            device_type=device.device_type,
            name=device.name,
            status=device.status
        )
        
        # Broadcast device creation
        await manager.broadcast(json.dumps({
            "type": "device_created",
            "data": {
                "id": str(db_device.id),
                "device_id": db_device.device_id,
                "name": db_device.name,
                "device_type": db_device.device_type,
                "status": db_device.status,
                "latitude": device.latitude,
                "longitude": device.longitude
            }
        }))
        
        # Convert to response model
        return DeviceResponse(
            id=db_device.id,
            device_type=db_device.device_type,
            device_id=db_device.device_id,
            name=db_device.name,
            status=db_device.status,
            altitude=db_device.altitude,
            heading=db_device.heading,
            speed=db_device.speed,
            battery_level=db_device.battery_level,
            signal_strength=db_device.signal_strength,
            latitude=device.latitude,
            longitude=device.longitude,
            last_seen=db_device.last_seen,
            created_at=db_device.created_at,
            updated_at=db_device.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create device: {str(e)}"
        )

@app.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    skip: int = 0,
    limit: int = 100,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all devices with optional filtering"""
    try:
        query = db.query(Device)
        
        if device_type:
            query = query.filter(Device.device_type == device_type)
        
        if status:
            query = query.filter(Device.status == status)
        
        devices = query.offset(skip).limit(limit).all()
        
        # Convert to response models
        device_responses = []
        for device in devices:
            # Extract coordinates from geometry
            from geoalchemy2.functions import ST_X, ST_Y
            longitude = db.scalar(ST_X(device.location))
            latitude = db.scalar(ST_Y(device.location))
            
            device_responses.append(DeviceResponse(
                id=device.id,
                device_type=device.device_type,
                device_id=device.device_id,
                name=device.name,
                status=device.status,
                altitude=device.altitude,
                heading=device.heading,
                speed=device.speed,
                battery_level=device.battery_level,
                signal_strength=device.signal_strength,
                latitude=latitude,
                longitude=longitude,
                last_seen=device.last_seen,
                created_at=device.created_at,
                updated_at=device.updated_at
            ))
        
        return device_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve devices: {str(e)}"
        )

@app.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific device by ID"""
    try:
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Extract coordinates from geometry
        from geoalchemy2.functions import ST_X, ST_Y
        longitude = db.scalar(ST_X(device.location))
        latitude = db.scalar(ST_Y(device.location))
        
        return DeviceResponse(
            id=device.id,
            device_type=device.device_type,
            device_id=device.device_id,
            name=device.name,
            status=device.status,
            altitude=device.altitude,
            heading=device.heading,
            speed=device.speed,
            battery_level=device.battery_level,
            signal_strength=device.signal_strength,
            latitude=latitude,
            longitude=longitude,
            last_seen=device.last_seen,
            created_at=device.created_at,
            updated_at=device.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve device: {str(e)}"
        )

@app.put("/devices/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator_or_higher)
):
    """Update a device"""
    try:
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Update fields
        if device_update.name is not None:
            device.name = device_update.name
        if device_update.status is not None:
            device.status = device_update.status
        if device_update.altitude is not None:
            device.altitude = device_update.altitude
        if device_update.heading is not None:
            device.heading = device_update.heading
        if device_update.speed is not None:
            device.speed = device_update.speed
        if device_update.battery_level is not None:
            device.battery_level = device_update.battery_level
        if device_update.signal_strength is not None:
            device.signal_strength = device_update.signal_strength
        
        # Update location if provided
        if device_update.latitude is not None and device_update.longitude is not None:
            from geoalchemy2.functions import ST_GeomFromText
            device.location = ST_GeomFromText(
                f"POINT({device_update.longitude} {device_update.latitude})", 4326
            )
        
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
        
        # Update Redis cache
        if device_update.latitude is not None and device_update.longitude is not None:
            update_device_location(
                device_id,
                device_update.latitude,
                device_update.longitude,
                device_type=device.device_type,
                name=device.name,
                status=device.status
            )
        
        # Broadcast device update
        await manager.broadcast(json.dumps({
            "type": "device_updated",
            "data": {
                "id": str(device.id),
                "device_id": device.device_id,
                "name": device.name,
                "status": device.status
            }
        }))
        
        # Return updated device
        from geoalchemy2.functions import ST_X, ST_Y
        longitude = db.scalar(ST_X(device.location))
        latitude = db.scalar(ST_Y(device.location))
        
        return DeviceResponse(
            id=device.id,
            device_type=device.device_type,
            device_id=device.device_id,
            name=device.name,
            status=device.status,
            altitude=device.altitude,
            heading=device.heading,
            speed=device.speed,
            battery_level=device.battery_level,
            signal_strength=device.signal_strength,
            latitude=latitude,
            longitude=longitude,
            last_seen=device.last_seen,
            created_at=device.created_at,
            updated_at=device.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update device: {str(e)}"
        )

@app.delete("/devices/{device_id}")
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator_or_higher)
):
    """Delete a device"""
    try:
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        db.delete(device)
        db.commit()
        
        # Broadcast device deletion
        await manager.broadcast(json.dumps({
            "type": "device_deleted",
            "data": {
                "device_id": device_id
            }
        }))
        
        return {"message": "Device deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete device: {str(e)}"
        )

# Device telemetry endpoints
@app.post("/devices/{device_id}/telemetry", response_model=DeviceTelemetryResponse)
async def create_telemetry(
    device_id: str,
    telemetry: DeviceTelemetryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator_or_higher)
):
    """Create telemetry data for a device"""
    try:
        # Check if device exists
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Create location geometry
        from geoalchemy2.functions import ST_GeomFromText
        location = ST_GeomFromText(f"POINT({telemetry.longitude} {telemetry.latitude})", 4326)
        
        # Create telemetry record
        db_telemetry = DeviceTelemetry(
            device_id=device.id,
            location=location,
            altitude=telemetry.altitude,
            heading=telemetry.heading,
            speed=telemetry.speed,
            battery_level=telemetry.battery_level,
            signal_strength=telemetry.signal_strength,
            temperature=telemetry.temperature,
            humidity=telemetry.humidity,
            additional_data=telemetry.additional_data
        )
        
        db.add(db_telemetry)
        
        # Update device last_seen and location
        device.last_seen = datetime.utcnow()
        device.location = location
        if telemetry.altitude is not None:
            device.altitude = telemetry.altitude
        if telemetry.heading is not None:
            device.heading = telemetry.heading
        if telemetry.speed is not None:
            device.speed = telemetry.speed
        if telemetry.battery_level is not None:
            device.battery_level = telemetry.battery_level
        if telemetry.signal_strength is not None:
            device.signal_strength = telemetry.signal_strength
        
        db.commit()
        db.refresh(db_telemetry)
        
        # Update Redis cache
        update_device_location(
            device_id,
            telemetry.latitude,
            telemetry.longitude,
            altitude=telemetry.altitude,
            heading=telemetry.heading,
            speed=telemetry.speed,
            battery_level=telemetry.battery_level,
            signal_strength=telemetry.signal_strength
        )
        
        # Broadcast telemetry update
        await manager.broadcast(json.dumps({
            "type": "telemetry_update",
            "data": {
                "device_id": device_id,
                "latitude": telemetry.latitude,
                "longitude": telemetry.longitude,
                "altitude": telemetry.altitude,
                "battery_level": telemetry.battery_level,
                "signal_strength": telemetry.signal_strength,
                "timestamp": telemetry.timestamp.isoformat() if telemetry.timestamp else datetime.utcnow().isoformat()
            }
        }))
        
        return DeviceTelemetryResponse(
            id=db_telemetry.id,
            device_id=db_telemetry.device_id,
            altitude=db_telemetry.altitude,
            heading=db_telemetry.heading,
            speed=db_telemetry.speed,
            battery_level=db_telemetry.battery_level,
            signal_strength=db_telemetry.signal_strength,
            temperature=db_telemetry.temperature,
            humidity=db_telemetry.humidity,
            additional_data=db_telemetry.additional_data,
            latitude=telemetry.latitude,
            longitude=telemetry.longitude,
            timestamp=db_telemetry.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create telemetry: {str(e)}"
        )

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Real-time device locations endpoint
@app.get("/devices/locations/realtime")
async def get_realtime_locations(
    current_user = Depends(get_current_active_user)
):
    """Get real-time device locations from Redis"""
    try:
        locations = get_all_device_locations()
        return {
            "success": True,
            "data": locations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve real-time locations: {str(e)}"
        )

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("Device Management Service started successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
