import pytest

from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user, require_admin

def create_fake_user(role: str):
    return SimpleNamespace(
        id=1,
        email="test@example.com",
        is_active=True,
        role=role
    )

@pytest.fixture
def client_as_user():
    user = create_fake_user("user")
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.pop(get_current_user, None)
    
def user_post_product(client_as_user):
    response = client_as_user.post("/products/",
                                   json={
                                            "name": "Gorila Chair",
                                            "price": "1300",
                                            "stock": 5,
                                        })
    
    assert response.status_code == 403
    
def test_require_admin_requires_admin():
    admin = create_fake_user("admin")
    result = require_admin(current_user=admin)
    
    assert result.role == "admin"
    
def test_require_admin_reject_user():
    user = create_fake_user("user")
    
    with pytest.raises(HTTPException) as error:
        require_admin(current_user=user)
        
    assert error.value.status_code == 403