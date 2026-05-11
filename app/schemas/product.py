from pydantic import BaseModel
from typing import List

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    colors: List[str]
    images: List[str]
    stock: int


class ProductResponse(ProductCreate):
    id: int

    class Config:
        orm_mode = True