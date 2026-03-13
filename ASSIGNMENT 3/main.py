from fastapi import FastAPI
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Product List
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# ---------------- DAY 1 ----------------

# Get all products
@app.get("/products")
def show_products():
    return {"products": products, "total": len(products)}

# Filter by category
@app.get("/products/category/{category_name}")
def filter_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found"}
    return {"products": filtered}

# Show in-stock products
@app.get("/products/instock")
def instock_products():
    items = [p for p in products if p["in_stock"]]
    return {"products": items}

# ---------------- DAY 2 ----------------

# Filter by price
@app.get("/products/filter")
def filter_products(min_price: Optional[int] = Query(None), max_price: Optional[int] = Query(None)):
    result = products
    if min_price:
        result = [p for p in result if p["price"] >= min_price]
    if max_price:
        result = [p for p in result if p["price"] <= max_price]
    return result

# ---------------- DAY 4 ----------------

# Product model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


# POST /products
@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


# GET /products/audit
@app.get("/products/audit")
def product_audit():

    total_products = len(products)
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock),
        "out_of_stock_names": out_stock,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# PUT /products/discount
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price
            updated.append({"name": p["name"], "new_price": new_price})

    if not updated:
        return {"message": "No products found"}

    return {"updated_products": updated}


# GET product by id
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}


# PUT update product
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    return {"error": "Product not found"}


# DELETE product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}

    return {"error": "Product not found"}