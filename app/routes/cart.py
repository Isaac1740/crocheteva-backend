from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.cart import Cart
from app.schemas.cart import CartCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🛒 ADD TO CART
@router.post("/cart")
def add_to_cart(data: CartCreate, db: Session = Depends(get_db)):
    item = Cart(
        session_id=data.session_id,
        product_id=data.product_id,
        quantity=data.quantity,
        color=data.color
    )

    db.add(item)
    db.commit()

    return {"message": "Added to cart 🛒"}


# 🛒 VIEW CART
@router.get("/cart/{session_id}")
def get_cart(session_id: str, db: Session = Depends(get_db)):
    items = db.query(Cart).filter(Cart.session_id == session_id).all()
    return items


# 🛒 REMOVE ITEM
@router.delete("/cart/{item_id}")
def remove_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Cart).filter(Cart.id == item_id).first()

    if not item:
        return {"error": "Item not found"}

    db.delete(item)
    db.commit()

    return {"message": "Removed from cart ❌"}

# 🧹 CLEAR CART
@router.delete("/clear-cart/{session_id}")
def clear_cart(session_id: str, db: Session = Depends(get_db)):

    db.query(Cart).filter(
        Cart.session_id == session_id
    ).delete()

    db.commit()

    return {"message": "Cart cleared ✅"}