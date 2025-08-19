import redis
import json
import os
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

# Async Redis client for WebSocket support
async def get_async_redis():
    """Get async Redis client"""
    return redis.asyncio.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )

# Cache functions
def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """Set cache value with expiration"""
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

def get_cache(key: str) -> Optional[Any]:
    """Get cache value"""
    try:
        value = redis_client.get(key)
        if value is None:
            return None
        
        # Try to parse as JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    except Exception as e:
        print(f"Cache get error: {e}")
        return None

def delete_cache(key: str) -> bool:
    """Delete cache key"""
    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False

def clear_cache_pattern(pattern: str) -> bool:
    """Clear cache keys matching pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return bool(redis_client.delete(*keys))
        return True
    except Exception as e:
        print(f"Cache clear pattern error: {e}")
        return False

# Real-time communication functions
def publish_message(channel: str, message: Dict[str, Any]) -> bool:
    """Publish message to Redis channel"""
    try:
        message["timestamp"] = datetime.utcnow().isoformat()
        redis_client.publish(channel, json.dumps(message))
        return True
    except Exception as e:
        print(f"Publish error: {e}")
        return False

def subscribe_to_channel(channel: str):
    """Subscribe to Redis channel"""
    try:
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)
        return pubsub
    except Exception as e:
        print(f"Subscribe error: {e}")
        return None

# Device tracking functions
def update_device_location(device_id: str, latitude: float, longitude: float, **kwargs) -> bool:
    """Update device location in Redis"""
    try:
        key = f"device:location:{device_id}"
        data = {
            "device_id": device_id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        redis_client.setex(key, 300, json.dumps(data))  # 5 minutes TTL
        
        # Publish location update
        publish_message("device_updates", {
            "type": "location_update",
            "device_id": device_id,
            "data": data
        })
        
        return True
    except Exception as e:
        print(f"Device location update error: {e}")
        return False

def get_device_location(device_id: str) -> Optional[Dict[str, Any]]:
    """Get device location from Redis"""
    try:
        key = f"device:location:{device_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Get device location error: {e}")
        return None

def get_all_device_locations() -> List[Dict[str, Any]]:
    """Get all device locations from Redis"""
    try:
        pattern = "device:location:*"
        keys = redis_client.keys(pattern)
        locations = []
        
        for key in keys:
            data = redis_client.get(key)
            if data:
                locations.append(json.loads(data))
        
        return locations
    except Exception as e:
        print(f"Get all device locations error: {e}")
        return []

# Battlefield situation tracking
def update_battlefield_situation(situation_id: str, data: Dict[str, Any]) -> bool:
    """Update battlefield situation in Redis"""
    try:
        key = f"situation:{situation_id}"
        data["updated_at"] = datetime.utcnow().isoformat()
        redis_client.setex(key, 1800, json.dumps(data))  # 30 minutes TTL
        
        # Publish situation update
        publish_message("battlefield_updates", {
            "type": "situation_update",
            "situation_id": situation_id,
            "data": data
        })
        
        return True
    except Exception as e:
        print(f"Battlefield situation update error: {e}")
        return False

def get_battlefield_situation(situation_id: str) -> Optional[Dict[str, Any]]:
    """Get battlefield situation from Redis"""
    try:
        key = f"situation:{situation_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Get battlefield situation error: {e}")
        return None

# Air support tracking
def update_air_support_request(request_id: str, data: Dict[str, Any]) -> bool:
    """Update air support request in Redis"""
    try:
        key = f"air_support:{request_id}"
        data["updated_at"] = datetime.utcnow().isoformat()
        redis_client.setex(key, 3600, json.dumps(data))  # 1 hour TTL
        
        # Publish air support update
        publish_message("air_support_updates", {
            "type": "request_update",
            "request_id": request_id,
            "data": data
        })
        
        return True
    except Exception as e:
        print(f"Air support update error: {e}")
        return False

def get_air_support_request(request_id: str) -> Optional[Dict[str, Any]]:
    """Get air support request from Redis"""
    try:
        key = f"air_support:{request_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Get air support request error: {e}")
        return None

# User session management
def set_user_session(user_id: str, session_data: Dict[str, Any], expire: int = 1800) -> bool:
    """Set user session in Redis"""
    try:
        key = f"session:{user_id}"
        session_data["created_at"] = datetime.utcnow().isoformat()
        redis_client.setex(key, expire, json.dumps(session_data))
        return True
    except Exception as e:
        print(f"Set user session error: {e}")
        return False

def get_user_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user session from Redis"""
    try:
        key = f"session:{user_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Get user session error: {e}")
        return None

def delete_user_session(user_id: str) -> bool:
    """Delete user session from Redis"""
    try:
        key = f"session:{user_id}"
        return bool(redis_client.delete(key))
    except Exception as e:
        print(f"Delete user session error: {e}")
        return False

# Health check
def check_redis_health() -> bool:
    """Check if Redis is accessible"""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False

# Rate limiting
def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Check rate limit for a key"""
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        count = int(current)
        if count < limit:
            redis_client.incr(key)
            return True
        
        return False
    except Exception as e:
        print(f"Rate limit check error: {e}")
        return True  # Allow if Redis is down

# Cleanup expired keys
def cleanup_expired_keys() -> int:
    """Clean up expired keys (for maintenance)"""
    try:
        # This is a simple cleanup - in production, use Redis TTL
        pattern = "device:location:*"
        keys = redis_client.keys(pattern)
        expired_count = 0
        
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl == -1:  # No TTL set
                redis_client.expire(key, 300)  # Set 5 minutes TTL
            elif ttl == -2:  # Key doesn't exist
                expired_count += 1
        
        return expired_count
    except Exception as e:
        print(f"Cleanup error: {e}")
        return 0
