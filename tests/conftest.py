import os
import pytest

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url
from fastapi.testclient import TestClient
from app import models
from app.database import Base, get_db
from app.main import app
from pathlib import Path
from types import SimpleNamespace
from app.dependencies import get_current_user

BASE_DIR= Path(__file__).resolve().parent.parent
ENV_PATH= BASE_DIR / "env" / ".postgres.env"

load_dotenv(dotenv_path=ENV_PATH)

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL belum dikonfigurasi di file .env")

parsed_url = make_url(TEST_DATABASE_URL)

if parsed_url.database != "producthub_test":
    raise RuntimeError("Batal testing: nama database yang ditest bukan producthub_test")

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)  
    
@pytest.fixture
def admin_client(client):
    admin = SimpleNamespace(
        id=1,
        email="admin@example.com",
        is_active=True,
        role="admin"
    )
    
    app.dependency_overrides[get_current_user] = lambda: admin
    
    yield client
    
    app.dependency_overrides.pop(get_current_user, None)
    
@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()