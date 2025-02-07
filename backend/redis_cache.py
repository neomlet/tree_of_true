from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def init_redis():
    redis_client = redis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis_client), prefix="github-cache")