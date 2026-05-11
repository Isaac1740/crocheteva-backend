from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request

import razorpay
import os
from dotenv import load_dotenv

# 🧠 Load env variables
load_dotenv()
print("KEY:", os.getenv("RAZORPAY_KEY_ID"))
print("SECRET:", os.getenv("RAZORPAY_KEY_SECRET"))

# 🧠 Import models (VERY IMPORTANT for table creation)
import app.models.product
import app.models.cart
import app.models.order
import app.models.order_item

# 🧠 Import routes
from app.routes import product, cart, order

# 🧠 DB
from app.database import engine, Base

app = FastAPI()


# 🔥 CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📸 SERVE UPLOADED FILES
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 💰 RAZORPAY CLIENT
razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)

# 🧠 DB startup
@app.on_event("startup")
def startup():
    print("Connecting to DB...")
    Base.metadata.create_all(bind=engine)
    print("Connected ✅")

# 🧠 ROUTES
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)

# 🧠 TEST ROUTE
@app.get("/")
def home():
    return {"message": "Eva Crochet Backend Running 🧶🔥"}

# 💰 CREATE RAZORPAY ORDER
@app.post("/create-razorpay-order")
def create_razorpay_order(data: dict):

    amount = data.get("amount")

    razorpay_order = razorpay_client.order.create({
        "amount": amount * 100,  # Razorpay uses paise
        "currency": "INR",
        "payment_capture": 1
    })

    return {
        "order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"]
    }

# ✅ VERIFY PAYMENT
@app.post("/verify-payment")
async def verify_payment(request: Request):

    data = await request.json()

    try:

        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        })

        return {
            "success": True
        }

    except Exception as e:

        print("Verification Error:", e)

        return {
            "success": False
        }