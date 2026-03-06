from fastapi import FastAPI
app=FastAPI()

# Product List
products=[
    {"id": 1, "name": "Wireless Mouse", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Desk Lamp", "price": 599, "category": "Electronics", "in_stock": False},

    # Q1 Added products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

#Q1 Get all products
@app.get("/products")
def show_products():
    total_products=len(products)

    return {
        "products":products,
        "total":total_products
    }

#Q2 Filter by category
@app.get("/products/category/{category_name}")
def filter_category(category_name:str):
    filtered_products=[]

    for item in products:
        if item["category"].lower()==category_name.lower():
            filtered_products.append(item)

    if len(filtered_products)==0:
        return {"error":"No products found in this category"}

    return {
        "category":category_name,
        "products":filtered_products,
        "total":len(filtered_products)
    }
# Q3 Show in-stock products
@app.get("/products/instock")
def instock_products():
    available_products=[]
    for item in products:
        if item["in_stock"]==True:
            available_products.append(item)
    return {
        "in_stock_products":available_products,
        "count": len(available_products)
    }


# Q4 – Store summary
@app.get("/store/summary")
def store_summary():
    total_products=len(products)

    in_stock_count=0
    categories=[]

    for item in products:
        if item["in_stock"]==True:
            in_stock_count+=1

        if item["category"] not in categories:
            categories.append(item["category"])

    out_of_stock=total_products-in_stock_count

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock,
        "categories": categories
    }

#Q5 Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword:str):
    matched_products=[]
    for item in products:
        if keyword.lower() in item["name"].lower():
            matched_products.append(item)

    if len(matched_products)==0:
        return {"message":"No products matched your search"}

    return {
        "keyword":keyword,
        "results":matched_products,
        "total_matches":len(matched_products)
    }


#Cheapest and most expensive product
@app.get("/products/deals")
def product_deals():
    cheapest=products[0]
    expensive=products[0]

    for item in products:
        if item["price"]<cheapest["price"]:
            cheapest=item
        if item["price"]>expensive["price"]:
            expensive=item
    return {
        "best_deal":cheapest,
        "premium_pick": expensive
    }