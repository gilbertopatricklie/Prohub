from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas import ProductCreation, ProductResponse, ProductUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

#yang ini response_model = list[ProductResponse] karna yang direturn itu list (banyak item produk)
@router.get("/", response_model= list[ProductResponse])
def get_all_product(db: Session = Depends(get_db)):
    statement = select(Product)
    result = db.scalars(statement).all()
    
    return result

#yang ini response_model = ProductResponse karna yang direturn satu item saja (pencarian by id)
@router.get("/{product_id}", response_model= ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product id not found/exist")
    
    return product

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreation, db: Session = Depends(get_db)):
    new_product = Product(
        name = payload.name,
        price = payload.price,
        stock = payload.stock
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_by_id(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product id not found/exist")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    statement = select(Product).where(Product.id == product_id)
    product = db.scalars(statement).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product id not found/exist")
    
    db.delete(product)
    db.commit()
    
    return None