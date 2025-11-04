#!/usr/bin/env python3
"""
Redis Configuration for High-Volume Optimization
Enterprise-grade caching, session management, and performance optimization
"""

import redis
import json
import pickle
from typing import Any, Optional, Dict, List
from functools import wraps
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisManager:
    """Enterprise Redis Manager for high-volume applications"""
    
    def __init__(self, host=None, port=None, db=None, password=None):
        """Initialize Redis connection with connection pooling"""
        # Use environment variables if not provided
        import os
        host = host or os.getenv('REDIS_HOST', 'localhost')
        port = port or int(os.getenv('REDIS_PORT', '6379'))
        db = db or int(os.getenv('REDIS_DB', '0'))
        password = password or os.getenv('REDIS_PASSWORD')
        
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=50,  # High connection pool for large volume
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30
        )
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection established successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    def get_client(self):
        """Get Redis client instance"""
        return self.redis_client
    
    def cache_key(self, prefix: str, *args) -> str:
        """Generate standardized cache key"""
        key_parts = [str(arg) for arg in args]
        return f"{prefix}:{':'.join(key_parts)}"
    
    # === CACHING METHODS ===
    
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache with TTL (default 1 hour)"""
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return pickle.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0
    
    # === SESSION MANAGEMENT ===
    
    def set_session(self, session_id: str, data: Dict, ttl: int = 86400) -> bool:
        """Set user session (default 24 hours)"""
        session_key = self.cache_key("session", session_id)
        return self.set_cache(session_key, data, ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get user session"""
        session_key = self.cache_key("session", session_id)
        return self.get_cache(session_key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete user session"""
        session_key = self.cache_key("session", session_id)
        return self.delete_cache(session_key)
    
    # === API RESPONSE CACHING ===
    
    def cache_api_response(self, endpoint: str, params: str, response: Any, ttl: int = 300) -> bool:
        """Cache API response (default 5 minutes)"""
        cache_key = self.cache_key("api", endpoint, params)
        return self.set_cache(cache_key, response, ttl)
    
    def get_cached_api_response(self, endpoint: str, params: str) -> Optional[Any]:
        """Get cached API response"""
        cache_key = self.cache_key("api", endpoint, params)
        return self.get_cache(cache_key)
    
    # === USER-SPECIFIC CACHING ===
    
    def cache_user_data(self, user_id: int, data_type: str, data: Any, ttl: int = 1800) -> bool:
        """Cache user-specific data (default 30 minutes)"""
        cache_key = self.cache_key("user", user_id, data_type)
        return self.set_cache(cache_key, data, ttl)
    
    def get_cached_user_data(self, user_id: int, data_type: str) -> Optional[Any]:
        """Get cached user-specific data"""
        cache_key = self.cache_key("user", user_id, data_type)
        return self.get_cache(cache_key)
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cache for a specific user"""
        pattern = f"user:{user_id}:*"
        return self.invalidate_pattern(pattern)
    
    # === RATE LIMITING ===
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if request is within rate limit"""
        key = self.cache_key("rate_limit", identifier)
        try:
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, window)
            return current <= limit
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    # === REAL-TIME FEATURES ===
    
    def publish_event(self, channel: str, data: Dict) -> bool:
        """Publish real-time event"""
        try:
            message = json.dumps(data)
            return self.redis_client.publish(channel, message) > 0
        except Exception as e:
            logger.error(f"Event publish error: {e}")
            return False
    
    def subscribe_to_events(self, channels: List[str], callback):
        """Subscribe to real-time events"""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(*channels)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    callback(message['channel'], data)
        except Exception as e:
            logger.error(f"Event subscription error: {e}")
    
    # === PERFORMANCE MONITORING ===
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info),
                'total_commands_processed': info.get('total_commands_processed', 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Global Redis manager instance
redis_manager = RedisManager()

# === CACHING DECORATORS ===

def cache_result(ttl: int = 300, key_prefix: str = "func"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = redis_manager.cache_key(
                key_prefix, 
                func.__name__, 
                str(args), 
                str(sorted(kwargs.items()))
            )
            
            # Try to get from cache
            cached_result = redis_manager.get_cache(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_manager.set_cache(cache_key, result, ttl)
            logger.info(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

def cache_user_data(ttl: int = 1800):
    """Decorator to cache user-specific data"""
    def decorator(func):
        @wraps(func)
        def wrapper(user_id: int, *args, **kwargs):
            cache_key = redis_manager.cache_key(
                "user_func", 
                func.__name__, 
                user_id,
                str(args), 
                str(sorted(kwargs.items()))
            )
            
            cached_result = redis_manager.get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(user_id, *args, **kwargs)
            redis_manager.set_cache(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# === EXPORT ===
__all__ = ['redis_manager', 'cache_result', 'cache_user_data', 'RedisManager']
