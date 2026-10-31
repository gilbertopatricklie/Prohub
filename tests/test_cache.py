import redis
import json

from app.redis_client import redis_client, get_cache, set_cache, delete_cache
from app.routers import products as products_route

def test_get_cache_success(monkeypatch):
    def mock_get(key):
        return "cached-data"
    
    monkeypatch.setattr(redis_client, "get", mock_get)
    result = get_cache("products:all")
    assert result == "cached-data"
    
def test_get_cache_fail(monkeypatch):
    def mock_get(key):
        raise redis.exceptions.ConnectionError("Redis Unavailable")
    
    monkeypatch.setattr(redis_client, "get", mock_get)
    result = get_cache("products:all")
    assert result is None
    
def test_set_cache_success(monkeypatch):
    calls = []
    
    def mock_set(key, value, ex):
        calls.append((key, value, ex))
        
    monkeypatch.setattr(redis_client, "set", mock_set)
    
    set_cache("products:all", "test-data", 120)
    
    assert calls == [("products:all", "test-data", 120)]
    
def test_set_cache_fail(monkeypatch):
    def mock_set(key, value, ex):
        raise redis.exceptions.ConnectionError("Redis unavailable")
    
    monkeypatch.setattr(redis_client, "set", mock_set)
    
    set_cache("products:all", "test-data", 120)
    
def test_delete_cache_success(monkeypatch):
    calls = []
    
    def mock_delete(*keys):
        calls.append(keys)
        
    monkeypatch.setattr(redis_client, "delete", mock_delete)
    
    delete_cache("products:all", "products:1")
    
    assert calls == [("products:all", "products:1")]
    
def test_delete_cache_fail(monkeypatch):
    def mock_delete(*keys):
        raise redis.exceptions.ConnectionError("Redis unavailable")
    
    monkeypatch.setattr(redis_client, "delete", mock_delete)
    
    delete_cache("products:all")
    
def test_products_cache_hit(admin_client, monkeypatch):
    cached_data = [
        {
            "id": 1,
            "name": "Cached Product",
            "price": "19.99",
            "stock": 5,
        }
    ]
    
    monkeypatch.setattr(products_route, "get_cache", lambda key: json.dumps(cached_data))
    
    def unexpected_set_cache(*args, **kwargs):
        raise AssertionError("set_cache harusnya tidak dipanggil.")
    
    monkeypatch.setattr(products_route, "set_cache", unexpected_set_cache)
    
    response = admin_client.get("/products/")
    
    assert response.status_code == 200
    assert response.json() == cached_data
    
def test_get_products_cache_miss(admin_client, monkeypatch):
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Database Product",
            "price": "29.99",
            "stock": 10,
        },
    )
    
    assert create_response.status_code == 201
    
    monkeypatch.setattr(products_route, "get_cache", lambda key: None)
    
    saved_cache = {}
    
    def mock_set_cache(key, value, ttl=120):
        saved_cache[key] = {
            "value": value,
            "ttl": ttl
        }
    
    monkeypatch.setattr(products_route, "set_cache", mock_set_cache)
    
    response = admin_client.get("/products/")
    
    assert response.status_code == 200
    
    products = response.json()
    
    assert any(product["name"] == "Database Product" for product in products)
    assert "products:skip:0:limit:10" in saved_cache
    
    cached_products = json.loads(saved_cache["products:skip:0:limit:10"]["value"])
    assert any(product["name"] == "Database Product" for product in cached_products)
    assert saved_cache["products:skip:0:limit:10"]["ttl"] == 120
    
def test_update_product_invalidates_cache(admin_client, monkeypatch):
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Keyboard",
            "price": "100.00",
            "stock": 10,
        },
    )
    
    assert create_response.status_code == 201
    
    product_id = create_response.json()["id"]
    deleted_keys = []
    
    def mock_delete_cache(*keys):
        deleted_keys.extend(keys)
        
    monkeypatch.setattr(products_route, "delete_cache", mock_delete_cache)
    
    response = admin_client.patch(
        f"/products/{product_id}",
        json={"price": "150.00"},
    )

    assert response.status_code == 200
    assert "products:all" in deleted_keys
    assert f"products:{product_id}" in deleted_keys
    
def test_delete_product_invalidates_cache(admin_client, monkeypatch):
    create_response = admin_client.post(
        "/products/",
        json={
            "name": "Mouse",
            "price": "50.00",
            "stock": 5,
        },
    )
    
    assert create_response.status_code == 201
    
    product_id = create_response.json()["id"]
    
    deleted_keys = []
    
    def mock_delete_cache(*keys):
        deleted_keys.extend(keys)
        
    monkeypatch.setattr(products_route, "delete_cache", mock_delete_cache)
    
    response = admin_client.delete(f"/products/{product_id}")
    assert response.status_code == 204
    assert "products:all" in deleted_keys
    assert f"products:{product_id}" in deleted_keys