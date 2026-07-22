"""
FastAPI server for web application.
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from webapp.database import (
    get_all_products,
    get_products_by_category,
    get_categories,
    get_product,
    update_product_stock,
    save_order
)

# ========== Configuration ==========
BOT_TOKEN = "1710690017:CAE8nJwnoUg8og-zWT0OUsQONB3t6nSfIoY"
SELLER_ID = 765254888
BOT_USERNAME = "shop_testbot"

# ========== FastAPI App ==========
app = FastAPI(title="Shop Web App", description="Web interface for shop bot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
app.mount("/images", StaticFiles(directory="products_images"), name="images")

# Templates
templates = Jinja2Templates(directory="webapp/templates")

# ========== Pydantic Models ==========
class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    customer_note: Optional[str] = None
    items: List[OrderItem]
    total_price: int

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    description: Optional[str] = None
    price: int
    stock: int
    image_url: Optional[str] = None

# ========== API Endpoints ==========

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Publlic page
    """
    categories = get_categories()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories,
            "bot_username": BOT_USERNAME
        }
    )

@app.get("/api/categories")
async def api_categories():
    """
    Get all categories.
    """
    categories = get_categories()
    return {"categories": categories}

@app.get("/api/products", response_model=List[ProductResponse])
async def api_products(category: Optional[str] = None):
    """
    Get all products or products by category.
    """
    if category:
        products = get_products_by_category(category)
    else:
        products = get_all_products()
    
    return products

@app.get("/api/product/{product_id}", response_model=ProductResponse)
async def api_product(product_id: int):
    """
    Get a single product by ID.
    """
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/order")
async def create_order(order: OrderRequest):
    """
    Save orders in database
    """
    try:
        for item in order.items:
            product = get_product(item.product_id)
            if not product:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": f"محصول با شناسه {item.product_id} یافت نشد."}
                )
            if product['stock'] < item.quantity:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": f"موجودی {product['name']} کافی نیست."}
                )
        
        db_items = []
        for item in order.items:
            product = get_product(item.product_id)
            db_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": product['price']
            })
        
        order_id = save_order(
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            customer_note=order.customer_note,
            items=db_items,
            total_price=order.total_price
        )
        
        if not order_id:
            raise Exception("خطا در ذخیره دیتابیس")

        return {
            "success": True,
            "message": "✅ سفارش شما با موفقیت ثبت شد.",
            "order_id": str(order_id)
        }
        
    except Exception as e:
        print(f"Error creating order: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"❌ خطا در ثبت سفارش: {str(e)}" if str(e) else "❌ خطا در ثبت سفارش. لطفاً مجدداً تلاش کنید."}
        )
    
# ========== Static file serving for images ==========
@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve product images.
    """
    from fastapi.responses import FileResponse
    filepath = os.path.join("products_images", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return JSONResponse(status_code=404, content={"error": "Image not found"})

# ========== Run with: uvicorn webapp.main:app --reload ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)