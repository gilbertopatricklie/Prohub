from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user, require_admin
from app.models import Product
from app.redis_client import delete_cache
from app.routers import products as product_route

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
    
def test_get_all_product_pagination(admin_client: TestClient, db_session):
    
    delete_cache(
        "products:skip:0:limit:5",
        "products:skip:5:limit:5",
    )

    for i in range(1, 16):
        product = Product(
            name=f"Product {i}",
            price=1000 * i,
            stock=i,
        )
        db_session.add(product)

    db_session.commit()

    response = admin_client.get("/products/?skip=0&limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 5

    response = admin_client.get("/products/?skip=5&limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 5

    first_page = admin_client.get("/products/?skip=0&limit=5").json()
    second_page = admin_client.get("/products/?skip=5&limit=5").json()
    first_page_ids = {product["id"] for product in first_page}
    second_page_ids = {product["id"] for product in second_page}

    assert first_page_ids.isdisjoint(second_page_ids)

    delete_cache(
        "products:skip:0:limit:5",
        "products:skip:5:limit:5",
    )
    
def test_get_all_product_sorting(admin_client, db_session, monkeypatch):
    monkeypatch.setattr(product_route, "get_cache", lambda key: None)
    monkeypatch.setattr(product_route, "set_cache", lambda key, value, ttl=120: None)
    
    products = [
        Product(name="Keyboard", price=500, stock=10),
        Product(name="Mouse", price=150, stock=20),
        Product(name="Monitor", price=2000, stock=5),
    ]
    
    db_session.add_all(products)
    db_session.commit()
    
    response_asc = admin_client.get("/products/?sort_by=price&order=asc")
    assert response_asc.status_code == 200
    
    products_asc = response_asc.json()
    
    assert [product["name"] for product in products_asc] == [
        "Mouse", "Keyboard", "Monitor"
    ]
    
    response_desc = admin_client.get("/products/?sort_by=price&order=desc")
    assert response_desc.status_code == 200
    
    products_desc = response_desc.json()
    
    assert [product["name"] for product in products_desc] == [
        "Monitor", "Keyboard", "Mouse"
    ]
    
def test_get_all_product_invalid_sort_column(admin_client):
    response = admin_client.get("/products/?sort_by=unknown&order=asc")
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sort column"
    
def test_get_all_product_invalid_sort_order(admin_client):
    response = admin_client.get("/products/?sort_by=id&order=unknown")
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sort order"
    
def test_get_all_product_filter_by_name(admin_client, db_session, monkeypatch):
    monkeypatch.setattr(product_route, "get_cache", lambda key: None)
    monkeypatch.setattr(product_route, "set_cache", lambda *args, **kwargs: None)
    
    products = [
        Product(name="Cloudx Headset", price=120, stock=11),
        Product(name="Cloudx Mousepad", price=30, stock=11),
        Product(name="Gaming Keyboard", price=500, stock=5),
    ]
    
    db_session.add_all(products)
    db_session.commit()
    
    response = admin_client.get("/products/?search=Cloudx")
    assert response.status_code == 200
    result = response.json()
    
    assert len(result) == 2
    assert all("Cloudx" in product["name"] for product in result)
    
def test_get_all_product_filter_case_insensitive(admin_client, db_session, monkeypatch):
    monkeypatch.setattr(product_route, "get_cache", lambda key: None)
    monkeypatch.setattr(product_route, "set_cache", lambda *args, **kwargs: None)
    
    db_session.add(Product(name="Cloudx Headset", price=120, stock=11))
    db_session.commit()
    
    response = admin_client.get("/products/?search=cloudx")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Cloudx Headset"
    
def test_get_product_filter_not_found(admin_client, db_session, monkeypatch):
    monkeypatch.setattr(product_route, "get_cache", lambda key: None)
    monkeypatch.setattr(product_route, "set_cache", lambda *args, **kwargs: None)
    
    db_session.add(Product(name="Cloudx Headset", price=120, stock=11))
    db_session.commit()
    
    response = admin_client.get("/products/?search=samsung")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
def test_get_all_product_combined_features(admin_client, db_session, monkeypatch):
    monkeypatch.setattr(product_route, "get_cache", lambda key: None)
    monkeypatch.setattr(product_route, "set_cache", lambda *args, **kwargs: None)
    
    products = [
        Product(name="Cloudx Headset", price=120, stock=11),
        Product(name="Cloudx Mousepad", price=30, stock=11),
        Product(name="Cloudx Keyboard", price=80, stock=5),
        Product(name="Gaming Mouse", price=50, stock=10),
        Product(name="Cloudx Monitor", price=500, stock=2),
    ]
    
    db_session.add_all(products)
    db_session.commit()
    
    response = admin_client.get("/products/?search=Cloudx&sort_by=price&order=asc&skip=0&limit=2")
    assert response.status_code == 200
    
    result = response.json()
    
    assert len(result) == 2
    assert [product["name"] for product in result] == [
        "Cloudx Mousepad", "Cloudx Keyboard"
    ]
    assert [product["price"] for product in result] == [
        "30.00", "80.00"
    ]