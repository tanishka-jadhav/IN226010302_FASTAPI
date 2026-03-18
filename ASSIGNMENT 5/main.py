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

@app.get("/products")
def show_products():
    return {"products": products, "total": len(products)}

@app.get("/products/category/{category_name}")
def filter_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found"}
    return {"products": filtered}

@app.get("/products/instock")
def instock_products():
    items = [p for p in products if p["in_stock"]]
    return {"products": items}

# ---------------- DAY 2 ----------------

@app.get("/products/filter")
def filter_products(min_price: Optional[int] = Query(None), max_price: Optional[int] = Query(None)):
    result = products
    if min_price:
        result = [p for p in result if p["price"] >= min_price]
    if max_price:
        result = [p for p in result if p["price"] <= max_price]
    return result

# ---------------- DAY 4 ----------------

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool

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

# ---------------- DAY 6 ----------------

@app.get("/products/search")
def search_products(keyword: str):

    matched = []
    for p in products:
        if keyword.lower() in p["name"].lower():
            matched.append(p)

    if len(matched) == 0:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(matched),
        "products": matched
    }

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False

    sorted_list = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_list
    }

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    total = len(products)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": products[start:end]
    }

@app.get("/products/sort-by-category")
def sort_by_category():
    return sorted(products, key=lambda x: (x["category"], x["price"]))

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": result[start:end]
    }

# ---------------- PRODUCT BY ID ----------------

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}

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

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}

    return {"error": "Product not found"}

# ---------------- DAY 5 ----------------

cart = []
orders = []

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"detail": "Product not found"}

    if not product["in_stock"]:
        return {"detail": f"{product['name']} is out of stock"}

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}

@app.get("/cart")
def view_cart():

    if len(cart) == 0:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    return {"error": "Item not found in cart"}

class Checkout(BaseModel):
    customer_name: str
    delivery_address: str

@app.post("/cart/checkout")
def checkout(data: Checkout):

    if len(cart) == 0:
        return {"detail": "CART_EMPTY"}

    created_orders = []
    total = 0

    for item in cart:

        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        created_orders.append(order)
        total += item["subtotal"]

    cart.clear()

    return {
        "orders_placed": created_orders,
        "grand_total": total
    }

@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }

@app.get("/orders/search")
def search_orders(customer_name: str):

    matched = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]

    if not matched:
        return {"message": "No orders found"}

    return {
        "customer_name": customer_name,
        "total_found": len(matched),
        "orders": matched
    }

@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total = len(orders)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": total,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }