from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(String(500))
    total_price = Column(Float)
    status = Column(String(50), default="Placed")
    payment_status = Column(String(50), default="Pending")