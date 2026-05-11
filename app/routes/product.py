from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()

# 🧠 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🧶 ADD PRODUCT
@router.post("/products", response_model=ProductResponse)
def add_product(data: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        colors=data.colors,
        images=data.images,
        stock=data.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# 🧶 GET ALL PRODUCTS
@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# 🧶 GET SINGLE PRODUCT
@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return product


# 🧶 DELETE PRODUCT (admin use)
@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    db.delete(product)
    db.commit()

    return {"message": "Product deleted ✅"}