import os
import jwt

from pathlib import Path
from pwdlib import PasswordHash
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

BASE_DIR= Path(__file__).resolve().parent.parent
ENV_PATH= BASE_DIR / "env" / ".env"

load_dotenv(dotenv_path=ENV_PATH)

SECRET_KEY= os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY belum dikonfigurasi di .env")

ALGORITHM= "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")
)

password_hash = PasswordHash.recommended()

#for registration
def hash_password(password: str) -> str:
    return password_hash.hash(password)

#for logging in
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }
    
    token = jwt.encode(
        payload, SECRET_KEY, algorithm=ALGORITHM
    )
    
    return token