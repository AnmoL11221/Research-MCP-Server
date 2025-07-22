import os
import json

try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_available = True
    try:
        redis_client.ping()
    except Exception:
        redis_available = False
except ImportError:
    redis_available = False

def get_from_cache(key: str):
    if redis_available:
        try:
            value = redis_client.get(key)
            if value is not None:
                return json.loads(value)
        except Exception:
            pass
    return None

def set_to_cache(key: str, value, ttl: int = 3600):
    if redis_available:
        try:
            redis_client.set(key, json.dumps(value), ex=ttl)
        except Exception:
            pass