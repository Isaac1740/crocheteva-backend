from sqlalchemy import Column, Integer, String, Float, JSON
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(500))
    price = Column(Float)
    category = Column(String(100))
    colors = Column(JSON)
    images = Column(JSON)
    stock = Column(Integer)