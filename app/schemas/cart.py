from pydantic import BaseModel

class CartCreate(BaseModel):
    session_id: str
    product_id: int
    quantity: int
    color: str