from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from fastapi import Request
import hmac
import hashlib
import json
import os

from app.database import SessionLocal
from app.models.cart import Cart
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.utils.email import send_email

router = APIRouter()


# 🧠 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📦 PLACE ORDER
@router.post("/place-order")
def place_order(
    session_id: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db)
):

    # 🛒 GET CART
    cart_items = db.query(Cart).filter(
        Cart.session_id == session_id
    ).all()

    if not cart_items:
        return {"error": "Cart is empty"}

    total = 0
    shipping_total = 0

    # 📦 CREATE ORDER
    order = Order(
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        total_price=0,
        status="Pending Verification",
        payment_status="Processing"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    items_text = ""

    # 🧶 LOOP ITEMS
    for item in cart_items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            continue

        product_total = product.price * item.quantity

        total += product_total

        # 🔥 SAFER CATEGORY MATCHING
        category = product.category.lower().strip()

        # 🚚 SHIPPING
        if category in ["keychain", "bookmark"]:
            shipping_total += 60 * item.quantity

        elif category == "bandana":
            shipping_total += 80 * item.quantity

        # 🧾 EMAIL TEXT
        items_text += (
            f"- {product.name} "
            f"({item.color}) "
            f"x {item.quantity} "
            f"(₹{product_total})\n"
        )

        # 📦 SAVE ORDER ITEMS
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

    # 💰 FINAL TOTAL
    final_total = total + shipping_total

    order.total_price = final_total

    db.commit()

    # 🧹 CLEAR CART
    db.query(Cart).filter(
        Cart.session_id == session_id
    ).delete()

    db.commit()

    return {"message": "Order placed successfully ✅"}


# ❌ CANCEL ORDER
@router.put("/cancel-order/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return {"error": "Order not found"}

    order.status = "Cancelled"

    db.commit()

    return {"message": "Order cancelled ❌"}


# 🔄 UPDATE ORDER STATUS
@router.put("/update-order-status/{order_id}")
def update_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return {"error": "Order not found"}

    order.status = status

    db.commit()

    return {"message": f"Order updated to {status} ✅"}


# 🔥 RAZORPAY WEBHOOK
@router.post("/razorpay-webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    body = await request.body()

    received_signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    webhook_secret = os.getenv(
        "RAZORPAY_WEBHOOK_SECRET"
    )

    generated_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    # ❌ INVALID WEBHOOK
    if generated_signature != received_signature:
        return {"status": "invalid signature"}

    payload = json.loads(body)

    event = payload.get("event")

    # ✅ PAYMENT SUCCESS
    if event == "payment.captured":

        payment = payload["payload"]["payment"]["entity"]

        print("✅ PAYMENT VERIFIED")
        print(payment)

        # ✅ GET LATEST PENDING ORDER
        order = (
            db.query(Order)
            .filter(Order.payment_status == "Processing")
            .order_by(Order.id.desc())
            .first()
        )

        if order:

            # ✅ UPDATE ORDER STATUS
            order.status = "Confirmed"
            order.payment_status = "Paid"

            db.commit()

            # ✅ ADMIN EMAIL
            send_email(
                "hello.evas.crochet26@gmail.com",
                "🧶 New Confirmed Order",
                f"""
🧶 NEW CONFIRMED ORDER

Customer Name: {order.full_name}
Phone: {order.phone}
Email: {order.email}

Address:
{order.address}

✅ Payment Verified Successfully
"""
            )

            # ✅ CUSTOMER EMAIL
            send_email(
                order.email,
                "Order Confirmed 🧶",
                f"""
Hi {order.full_name},

Your payment has been verified successfully 💖

Your order is now confirmed 🧶✨

Thank you for shopping with Eva Crochet 💕
"""
            )

        return {"status": "payment verified"}

    return {"status": "ignored"}