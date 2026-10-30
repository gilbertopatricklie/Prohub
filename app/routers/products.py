import json

from app.redis_client import get_cache, set_cache, delete_cache
from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas import ProductCreation, ProductResponse, ProductUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User
from app.dependencies import get_current_user, require_admin

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

#yang ini response_model = list[ProductResponse] karna yang direturn itu list (banyak item produk)
@router.get("/", response_model= list[ProductResponse])
def get_all_product(db: Session = Depends(get_db)):
    cache_key = "products:all"
    cached_products = get_cache(cache_key)
    
    #kalo ada cachenya pake dari redis
    if cached_products:
        return json.loads(cached_products)
    #kalo ga ada di cache, ambil dari database
    statement = select(Product)
    products = db.scalars(statement).all()
    
    products_data = [
        ProductResponse(
            id = product.id,
            name = product.name,
            price = product.price,
            stock = product.stock
        ).model_dump(mode="json") for product in products
    ]
    
    set_cache(
        cache_key,
        json.dumps(products_data),
        ttl=120
    )
    
    return products_data

#yang ini response_model = ProductResponse karna yang direturn satu item saja (pencarian by id)
@router.get("/{product_id}", response_model= ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"products:{product_id}"
    
    cached_product = get_cache(cache_key)
    
    if cached_product:
        return json.loads(cached_product)
    
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = ProductResponse(
        id = product.id,
        name = product.name,
        price = product.price,
        stock = product.stock
    ).model_dump(mode="json")
    
    set_cache(
        cache_key,
        json.dumps(product_data),
        ttl=120
    )
    
    return product_data

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreation, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    new_product = Product(
        name = payload.name,
        price = payload.price,
        stock = payload.stock
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    delete_cache("products:all")
    
    return new_product

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_by_id(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product id not found/exist")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.commit()
    db.refresh(product)
    delete_cache("products:all", f"products:{product_id}")
    
    return product

@router.delete("/{product_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_product_by_id(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product id not found/exist")
    
    db.delete(product)
    db.commit()
    delete_cache("products:all", f"products:{product_id}")
    
    return None