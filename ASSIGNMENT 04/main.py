# ---------------- DAY 5 ----------------

cart = []
orders = []


# Add item to cart
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# View cart
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


# Remove item from cart
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    return {"error": "Item not found in cart"}


# Checkout
class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


@app.post("/cart/checkout")
def checkout(data: Checkout):

    if len(cart) == 0:
        return {"error": "Cart is empty"}

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


# View orders
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }