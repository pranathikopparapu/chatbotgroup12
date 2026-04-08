from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from bson import ObjectId

# ================== 🔥 MONGODB ==================
try:
    client = MongoClient(
        "mongodb+srv://foodorder:food123@cluster0.xmgjudt.mongodb.net/?appName=Cluster0",
        serverSelectionTimeoutMS=5000
    )
    db = client["test"]
    collection = db["foods"]

    client.server_info()
    print("✅ MongoDB Connected")

except Exception as e:
    print("❌ MongoDB Error:", e)
    collection = None


# ================== 📁 PATH ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

print("📁 Frontend Path:", FRONTEND_DIR)


# ================== 🤖 HELPER ==================
def get_price(product):
    try:
        return float(product.get("finalPrice", product.get("price", 0)))
    except:
        return 0


# ================== 📦 STOCK MANAGEMENT ==================

def update_stock(product_id, quantity=1):
    try:
        product = collection.find_one({"_id": ObjectId(product_id)})
    except:
        return "not_found"

    if not product:
        return "not_found"

    stock = product.get("stock", 0)

    if not isinstance(stock, (int, float)):
        stock = 0

    if stock < quantity:
        return "out_of_stock"

    collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$inc": {
                "stock": -quantity,
                "sold": quantity
            }
        }
    )

    return "success"


def get_most_sold():
    products = list(collection.find())
    top = sorted(products, key=lambda x: x.get("sold", 0), reverse=True)[:5]

    return {
        "type": "text",
        "message": "🔥 Most Sold Items:\n" + "\n".join(
            [f"{p.get('name')} ({p.get('sold', 0)} sold)" for p in top]
        )
    }


def get_low_stock():
    products = list(collection.find())

    low_stock = [
        p for p in products
        if isinstance(p.get("stock"), (int, float)) and p.get("stock") <= 5
    ]

    if not low_stock:
        return {
            "type": "text",
            "message": "✅ All items have sufficient stock"
        }

    return {
        "type": "text",
        "message": "⚠️ Low Stock Items:\n" + "\n".join(
            [f"{p.get('name')} ({p.get('stock')} left)" for p in low_stock]
        )
    }


# ================== 📊 CHART FUNCTIONS ==================

# 🔥 CATEGORY-WISE STOCK (BEST)
def get_sales_summary():
    products = list(collection.find())

    data = {}

    for p in products:
        name = p.get("name", "Unknown")
        sold = p.get("sold", 0)

        if not isinstance(sold, (int, float)):
            sold = 0

        if sold > 0:
            data[name] = sold

    # 🔥 IF NO DATA → USE DUMMY
    if not data:
        data = {
            "Pizza": 25,
            "Burger": 18,
            "Milkshake": 12,
            "Sandwich": 10
        }

    return {
        "type": "chart",
        "chartData": {
            "categories": data
        }
    }   
# 🔥 CATEGORY-WISE SALES
def category_sales():
    products = list(collection.find())
    data = {}

    for p in products:
        cat = p.get("category", "Others")
        sold = p.get("sold", 0)

        if not isinstance(sold, (int, float)):
            sold = 0

        if sold > 0:
            data[cat] = data.get(cat, 0) + sold

    # 🔥 DUMMY DATA
    if not data:
        data = {
            "Pizza": 30,
            "Burger": 20,
            "Milkshake": 15
        }

    return {
        "type": "chart",
        "chartData": {
            "categories": data
        }
    }


# ================== 🤖 CHATBOT ==================
def get_product_answer(query):
    if collection is None:
        return {"type": "text", "message": "⚠️ DB not connected"}

    query = query.lower().strip()
    print("User Query:", query)

    words = query.split()
    products = list(collection.find())

    if not products:
        return {"type": "text", "message": "No products available"}

    def match_score(name):
        name = name.lower()
        return sum(1 for w in words if w in name)

    # 🔥 MOST SOLD
    if any(phrase in query for phrase in ["most sold", "trending", "top selling"]):
        return get_most_sold()

    # ⚠️ LOW STOCK
    if any(phrase in query for phrase in ["low stock", "stock alert", "low inventory"]):
        return get_low_stock()

    # 📊 STOCK SUMMARY
    if any(phrase in query for phrase in ["stock summary", "sales summary", "orders", "report"]):
        return get_sales_summary()
    
  
   
    

    # 📈 CATEGORY SALES
    if "sales by category" in query:
        return category_sales()

    # 🛒 ADD TO CART
    if any(word in query for word in ["add", "buy", "cart"]):
        best = max(products, key=lambda p: match_score(p.get("name", "")))

        if match_score(best.get("name", "")) == 0:
            return {"type": "text", "message": "❌ Product not found"}

        result = update_stock(best.get("_id"))

        if result == "out_of_stock":
            return {
                "type": "text",
                "message": f"❌ {best.get('name')} is out of stock"
            }

        return {
            "type": "add_to_cart",
            "product": {
                "_id": str(best.get("_id")),
                "name": best.get("name"),
                "price": get_price(best),
                "image": best.get("image"),
            }
        }

    # 💎 PREMIUM
    if any(word in query for word in ["best", "expensive", "premium"]):
        expensive = sorted(products, key=get_price, reverse=True)[:3]
        return {
            "type": "text",
            "message": "💎 Premium items:\n" + "\n".join(
                [f"{p.get('name')} ₹{get_price(p)}" for p in expensive]
            )
        }

    # ⭐ RECOMMEND
    if "recommend" in query:
        top = sorted(products, key=lambda x: x.get("avgRating", 0), reverse=True)[:3]
        return {
            "type": "text",
            "message": "⭐ Recommended:\n" + "\n".join(
                [p.get("name") for p in top]
            )
        }

    # 💰 CHEAP
    if any(word in query for word in ["cheap", "budget", "low price"]):
        cheapest = min(products, key=get_price)
        return {
            "type": "text",
            "message": f"💰 Cheapest: {cheapest.get('name')} ₹{get_price(cheapest)}"
        }

    # 🔍 SEARCH
    best = max(products, key=lambda p: match_score(p.get("name", "")))

    if match_score(best.get("name", "")) > 0:
        return {
            "type": "text",
            "message": f"🍽️ {best.get('name')} ₹{get_price(best)}"
        }

    return {
        "type": "text",
        "message": "🤖 Try: add kitkat, most sold, low stock, inventory summary"
    }


# ================== 🚀 FASTAPI ==================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== STATIC ==================
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def home():
    index_path = os.path.join(FRONTEND_DIR, "index.html")

    if not os.path.exists(index_path):
        return {"error": "index.html not found ❌"}

    return FileResponse(index_path)


# ================== API ==================
class Query(BaseModel):
    question: str


@app.post("/chat")
def chat(query: Query):
    return get_product_answer(query.question)