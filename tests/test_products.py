from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user, require_admin

def create_fake_admin():
    return SimpleNamespace(
        id=1,
        email="admin@example.com",
        is_active=True,
        role="admin"
    )
    
def test_create_and_read_product(admin_client: TestClient):
    admin = create_fake_admin()
    
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin
    
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Keyboard Vortex Series",
            "price": "60",
            "stock": 15,
        },
    )
    
    assert create_response.status_code == 201
    created_product = create_response.json()
    
    assert created_product["name"] == "Keyboard Vortex Series"
    assert created_product["stock"] == 15
    assert "id" in created_product
    
    product_id = created_product["id"]
    read_response = admin_client.get(f"/products/{product_id}")
    
    assert read_response.status_code == 200
    retrieved_products = read_response.json()
    
    assert retrieved_products["id"] == product_id
    assert retrieved_products["name"] == "Keyboard Vortex Series"
    assert retrieved_products["stock"] == 15
    
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)
        
def test_update_product(admin_client: TestClient):
    admin = create_fake_admin()
    
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin
    
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Mouse Votre",
            "price": "30",
            "stock": 5,
        },
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    update_response = admin_client.patch(
        f"/products/{product_id}",
        json={
            "price": "29.99",
            "stock": 4,
        },
    )
    
    assert update_response.status_code == 200
    updated_product = update_response.json()
    
    assert updated_product["id"] == product_id
    assert updated_product["price"] == "29.99"
    assert updated_product["stock"] == 4
    
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)
        
def test_delete_product(admin_client: TestClient):
    admin = create_fake_admin()
    
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin
    
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Monitor Xiaomi",
            "price": "1299.99",
            "stock": 3,
        },
    )
    
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    delete_response = admin_client.delete(
        f"/products/{product_id}"
    )
    
    read_response = admin_client.get(
        f"/products/{product_id}"
    )
    
    assert read_response.status_code == 404
    
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)