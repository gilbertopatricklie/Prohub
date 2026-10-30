import os
import redis
import logging

from redis.exceptions import RedisError
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR= Path(__file__).resolve().parent.parent
ENV_PATH= BASE_DIR / "env" / ".env" 

load_dotenv(dotenv_path=ENV_PATH)

REDIS_URL= os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL belum dikonfigurasi di file .env")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

#==================Helper Function==================#
def get_cache(key: str):
    try:
        return redis_client.get(key)
    except RedisError:
        logger.exception("Redis GET gagal: %s", key)
        return None

def set_cache(key: str, value: str, ttl: int):
    try:
        redis_client.set(key, value, ex=ttl)
    except RedisError:
        logger.exception("Redis SET gagal: %s", key)
        
def delete_cache(*keys: str):
    try:
        redis_client.delete(*keys)
    except RedisError:
        logger.exception("Redis DEL gagal: %s", keys)
