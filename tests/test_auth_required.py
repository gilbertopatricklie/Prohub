from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_products():
    response = client.get("/products/")
    assert response.status_code == 200
    
def test_get_products_by_id():
    response = client.get("/products/1")
    assert response.status_code == 200
    
def test_current_user_require_authentication():
    response = client.get("/auth/me")
    assert response.status_code == 401