from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum
from geoalchemy2 import WKBElement
from shapely.geometry import Point
import json

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    INTELLIGENCE = "intelligence"
    COMMANDER = "commander"

# Base models
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

class PaginatedResponse(BaseResponse):
    total: int = 0
    page: int = 1
    size: int = 10
    pages: int = 0

# User models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    role: UserRole = UserRole.OPERATOR
    rank: Optional[str] = None
    unit: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    role: Optional[UserRole] = None
    rank: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Device models
class DeviceBase(BaseModel):
    device_type: str = Field(..., min_length=1, max_length=100)
    device_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    status: DeviceStatus = DeviceStatus.ACTIVE
    altitude: Optional[float] = Field(None, ge=0, le=50000)
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0, le=1000)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = Field(None, ge=0, le=100)

class DeviceCreate(DeviceBase):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[DeviceStatus] = None
    altitude: Optional[float] = Field(None, ge=0, le=50000)
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0, le=1000)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = Field(None, ge=0, le=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class DeviceResponse(DeviceBase):
    id: UUID
    latitude: float
    longitude: float
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Intelligence models
class IntelligenceReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    threat_level: ThreatLevel
    source: Optional[str] = None
    confidence_level: int = Field(..., ge=1, le=10)

class IntelligenceReportCreate(IntelligenceReportBase):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class IntelligenceReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    threat_level: Optional[ThreatLevel] = None
    source: Optional[str] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class IntelligenceReportResponse(IntelligenceReportBase):
    id: UUID
    latitude: float
    longitude: float
    status: str
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Communication models
class CommunicationBase(BaseModel):
    recipient_id: UUID
    message_type: str = Field(..., min_length=1, max_length=50)
    subject: Optional[str] = None
    content: str = Field(..., min_length=1)
    priority: Priority = Priority.NORMAL

class CommunicationCreate(CommunicationBase):
    pass

class CommunicationUpdate(BaseModel):
    subject: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[str] = None

class CommunicationResponse(CommunicationBase):
    id: UUID
    sender_id: UUID
    status: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Air Support models
class AirSupportRequestBase(BaseModel):
    request_type: str = Field(..., min_length=1, max_length=100)
    priority: Priority
    target_description: Optional[str] = None
    notes: Optional[str] = None

class AirSupportRequestCreate(AirSupportRequestBase):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class AirSupportRequestUpdate(BaseModel):
    request_type: Optional[str] = Field(None, min_length=1, max_length=100)
    priority: Optional[Priority] = None
    target_description: Optional[str] = None
    status: Optional[str] = None
    assigned_aircraft: Optional[str] = None
    eta: Optional[datetime] = None
    notes: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class AirSupportRequestResponse(AirSupportRequestBase):
    id: UUID
    requester_id: UUID
    latitude: float
    longitude: float
    coordinates: str
    status: str
    assigned_aircraft: Optional[str] = None
    eta: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Battlefield Situation models
class BattlefieldSituationBase(BaseModel):
    situation_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    threat_level: Optional[ThreatLevel] = None
    friendly_forces: Optional[str] = None
    enemy_forces: Optional[str] = None
    civilian_presence: bool = False

class BattlefieldSituationCreate(BattlefieldSituationBase):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class BattlefieldSituationUpdate(BaseModel):
    situation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    threat_level: Optional[ThreatLevel] = None
    friendly_forces: Optional[str] = None
    enemy_forces: Optional[str] = None
    civilian_presence: Optional[bool] = None
    status: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class BattlefieldSituationResponse(BattlefieldSituationBase):
    id: UUID
    latitude: float
    longitude: float
    status: str
    reported_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Device Telemetry models
class DeviceTelemetryBase(BaseModel):
    altitude: Optional[float] = Field(None, ge=0, le=50000)
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0, le=1000)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=-50, le=100)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    additional_data: Optional[Dict[str, Any]] = None

class DeviceTelemetryCreate(DeviceTelemetryBase):
    device_id: UUID
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class DeviceTelemetryResponse(DeviceTelemetryBase):
    id: UUID
    device_id: UUID
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        from_attributes = True

# WebSocket message models
class WebSocketMessage(BaseModel):
    type: str
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DeviceUpdateMessage(WebSocketMessage):
    type: str = "device_update"
    data: DeviceResponse

class IntelligenceUpdateMessage(WebSocketMessage):
    type: str = "intelligence_update"
    data: IntelligenceReportResponse

class AirSupportUpdateMessage(WebSocketMessage):
    type: str = "air_support_update"
    data: AirSupportRequestResponse

class BattlefieldUpdateMessage(WebSocketMessage):
    type: str = "battlefield_update"
    data: BattlefieldSituationResponse

# Utility functions for geometry handling
def point_to_coordinates(point: WKBElement) -> tuple:
    """Convert PostGIS WKB point to (latitude, longitude) tuple"""
    if point is None:
        return None, None
    shapely_point = Point(point.data)
    return shapely_point.y, shapely_point.x

def coordinates_to_point(latitude: float, longitude: float) -> str:
    """Convert (latitude, longitude) to PostGIS POINT string"""
    return f"POINT({longitude} {latitude})"
