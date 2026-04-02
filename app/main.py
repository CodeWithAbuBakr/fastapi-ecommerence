from fastapi import FastAPI, Query, HTTPException, Path
from service.products import get_all_products

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

# @app.get("/products")
# def read_products():
#     return get_all_products()

@app.get("/products")
def list_products(name: str = Query(default=None, min_length=1, max_length=50, description="Name of the product to filter by"), 
                  sort_by_price: bool = Query(default=False, description="Whether to sort the products by price"), 
                  order: str = Query(default="asc", regex="^(asc|desc)$", description="Sort order (asc or desc)"), 
                  limit: int = Query(default=10, ge=1, le=100, description="Maximum number of products to return"),
                  offset: int = Query(default=0, ge=0, description="Number of products to skip before starting to collect the result set")):
    products = get_all_products()
    if name:
        needle = name.strip().lower()
        products = [ p for p in products if needle in p.get("name", "").lower() ]
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found with name containing '{name}' ")
    
    if sort_by_price:
        reverse = (order == "desc")
        products.sort(key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)
    products = products[offset : offset + limit]
    return {"total": total, "items": products}

@app.get("/products/{product_id}")
def get_product_by_id(product_id: str = Path(..., min_lenght=36, max_length=36, example="0005a4ea-ce3f-4dd7-bee0-f4ccc70fea6a", description="ID of the product to retrieve")):
    products = get_all_products()
    for p in products:
        if p.get("id") == product_id:
            return p
    raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")