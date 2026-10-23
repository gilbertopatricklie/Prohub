from pydantic import BaseModel, Field

class ProductCreation(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int