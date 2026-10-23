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
# @router.get("/{product_id}", response_model= ProductResponse)
# def get_product_by_id(product_id: int):
#     for product in products:
#         if product["id"] == product_id:
#             return product
        
#     raise HTTPException(status_code=404, detail="Product id not found.")

# @router.post("/", status_code=status.HTTP_201_CREATED)
# def create_product(product: ProductCreation):
#     new_product= product.model_dump()
#     new_product["id"] = max(
#         (item["id"] for item in products),
#         default=0
#     ) + 1
    
#     products.append(new_product)
    
#     return new_product

# @router.patch("/{product_id}", response_model=ProductResponse)
# def update_product_by_id(product_id: int, payload: ProductUpdate):
#     for product in products:
#         if product["id"] == product_id:
#             update_data = payload.model_dump(exclude_unset=True)
#             product.update(update_data)
#             return product