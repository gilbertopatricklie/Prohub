from pydantic import BaseModel, Field, ConfigDict, model_validator
from decimal import Decimal

class ProductCreation(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    stock: int = Field(ge=0)
    
class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2, max_digits=12)
    stock: int | None =Field(default=None, ge=0)
    
    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data):
        if isinstance(data, dict):
            for field in("name", "price", "stock"):
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
                
        return data
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int