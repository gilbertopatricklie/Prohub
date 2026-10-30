import os
import redis

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR= Path(__file__).resolve().parent.parent
ENV_PATH= BASE_DIR / "env" / ".env" 

load_dotenv(dotenv_path=ENV_PATH)

REDIS_URL= os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL belum dikonfigurasi di file .env")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

