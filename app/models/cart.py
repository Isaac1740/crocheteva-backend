from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    color = Column(String(50))