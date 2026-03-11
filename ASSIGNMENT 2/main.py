from fastapi import FastAPI
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Product List
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Desk Lamp", "price": 599, "category": "Electronics", "in_stock": False},

    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

# ---------------- DAY 1 ----------------

# Get all products
@app.get("/products")
def show_products():
    return {
        "products": products,
        "total": len(products)
    }


# Filter by category
@app.get("/products/category/{category_name}")
def filter_category(category_name: str):

    filtered_products = []

    for item in products:
        if item["category"].lower() == category_name.lower():
            filtered_products.append(item)

    if len(filtered_products) == 0:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products,
        "total": len(filtered_products)
    }


# Show in-stock products
@app.get("/products/instock")
def instock_products():

    available_products = []

    for item in products:
        if item["in_stock"]:
            available_products.append(item)

    return {
        "in_stock_products": available_products,
        "count": len(available_products)
    }


# Store summary
@app.get("/store/summary")
def store_summary():

    total_products = len(products)
    in_stock_count = 0
    categories = []

    for item in products:

        if item["in_stock"]:
            in_stock_count += 1

        if item["category"] not in categories:
            categories.append(item["category"])

    out_of_stock = total_products - in_stock_count

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock,
        "categories": categories
    }


# Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = []

    for item in products:
        if keyword.lower() in item["name"].lower():
            matched_products.append(item)

    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": matched_products,
        "total_matches": len(matched_products)
    }


# Cheapest and most expensive product
@app.get("/products/deals")
def product_deals():

    cheapest = products[0]
    expensive = products[0]

    for item in products:

        if item["price"] < cheapest["price"]:
            cheapest = item

        if item["price"] > expensive["price"]:
            expensive = item

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }


# ---------------- DAY 2 ----------------

# Q1 Filter by minimum price
@app.get("/products/filter")
def filter_products(
        category: Optional[str] = None,
        max_price: Optional[int] = None,
        min_price: Optional[int] = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return result


# Q2 Get only product price
@app.get("/products/{product_id}/price")
def product_price(product_id: int):

    for item in products:

        if item["id"] == product_id:
            return {
                "name": item["name"],
                "price": item["price"]
            }

    return {"error": "Product not found"}


# Q3 Feedback API

class CustomerFeedback(BaseModel):

    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


feedback = []


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }


# Q4 Product summary dashboard
@app.get("/products/summary")
def product_summary():

    in_stock_products = [p for p in products if p["in_stock"]]
    out_stock_products = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_products),
        "out_of_stock_count": len(out_stock_products),
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


# Q5 Bulk order system

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:

            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })

        elif not product["in_stock"]:

            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })

        else:

            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# BONUS Order tracking

orders = []


@app.post("/orders")
def create_order(product_id: int, quantity: int):

    order_id = len(orders) + 1

    new_order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:

        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:

        if order["order_id"] == order_id:
            order["status"] = "confirmed"

            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}