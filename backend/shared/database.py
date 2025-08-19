from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, UUID as SQLUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from typing import Generator
import os
from datetime import datetime
import uuid

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://c4isr_user:c4isr_password@localhost:5432/c4isr")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database dependency
def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database models
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="operator")
    rank = Column(String(50))
    unit = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_type = Column(String(100), nullable=False, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active", index=True)
    location = Column(Geometry("POINT", srid=4326), index=True)
    altitude = Column(Float)
    heading = Column(Float)
    speed = Column(Float)
    battery_level = Column(Integer)
    signal_strength = Column(Integer)
    last_seen = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class IntelligenceReport(Base):
    __tablename__ = "intelligence_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    threat_level = Column(String(50), nullable=False, index=True)
    location = Column(Geometry("POINT", srid=4326), index=True)
    source = Column(String(100))
    confidence_level = Column(Integer)
    status = Column(String(50), default="new", index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Communication(Base):
    __tablename__ = "communications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_type = Column(String(50), nullable=False)
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")
    status = Column(String(50), default="sent")
    sent_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AirSupportRequest(Base):
    __tablename__ = "air_support_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_type = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False, index=True)
    location = Column(Geometry("POINT", srid=4326), index=True)
    target_description = Column(Text)
    coordinates = Column(String(100))
    status = Column(String(50), default="pending", index=True)
    assigned_aircraft = Column(String(100))
    eta = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class BattlefieldSituation(Base):
    __tablename__ = "battlefield_situations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry("POINT", srid=4326), index=True)
    situation_type = Column(String(100), nullable=False)
    description = Column(Text)
    threat_level = Column(String(50), index=True)
    friendly_forces = Column(Text)
    enemy_forces = Column(Text)
    civilian_presence = Column(Boolean, default=False)
    status = Column(String(50), default="active", index=True)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class DeviceTelemetry(Base):
    __tablename__ = "device_telemetry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    location = Column(Geometry("POINT", srid=4326), index=True)
    altitude = Column(Float)
    heading = Column(Float)
    speed = Column(Float)
    battery_level = Column(Integer)
    signal_strength = Column(Integer)
    temperature = Column(Float)
    humidity = Column(Float)
    additional_data = Column(JSONB)

# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Get a database session"""
    return SessionLocal()

# Health check function
def check_db_health() -> bool:
    """Check if database is accessible"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception:
        return False
