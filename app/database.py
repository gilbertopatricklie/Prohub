import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR= Path(__file__).resolve().parent.parent
ENV_PATH= BASE_DIR / "env" / ".postgres.env"

load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL= os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Belum konfigurasi DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()