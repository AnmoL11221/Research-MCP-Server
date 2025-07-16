import redis
import os
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_from_cache(key: str):
    value = redis_client.get(key)
    if value is not None:
        return json.loads(value)
    return None

def set_to_cache(key: str, value, ttl: int):
    redis_client.setex(key, ttl, json.dumps(value))