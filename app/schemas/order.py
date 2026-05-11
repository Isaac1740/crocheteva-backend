from pydantic import BaseModel

class OrderCreate(BaseModel):
    session_id: str
    full_name: str
    email: str
    phone: str
    address: str