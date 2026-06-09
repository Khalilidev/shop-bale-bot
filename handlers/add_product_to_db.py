"""
Handler for adding products to database from Excel or single product.
"""

import sqlite3
import os
from datetime import datetime

DB_NAME = "database.db"


def convert_persian_to_english(text: str) -> str:
    """
    Convert Persian/Arabic numbers to English numbers.
    """
    persian_numbers = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_numbers.items():
        text = text.replace(persian, english)
    return text


def validate_price(price_str: str) -> int:
    """
    Validate and convert price to integer.
    """
    price_str = convert_persian_to_english(price_str)
    price_str = price_str.replace(',', '').replace(' ', '')
    
    if not price_str:
        raise ValueError("قیمت نمی‌تواند خالی باشد")
    
    price = int(price_str)
    
    if price <= 0:
        raise ValueError("قیمت باید بزرگتر از صفر باشد")
    
    return price


def validate_stock(stock_str: str) -> int:
    """
    Validate and convert stock to integer.
    """
    stock_str = convert_persian_to_english(stock_str)
    stock_str = stock_str.replace(',', '').replace(' ', '')
    
    if not stock_str:
        return 0
    
    stock = int(stock_str)
    
    if stock < 0:
        raise ValueError("موجودی نمی‌تواند منفی باشد")
    
    return stock


def get_default_brand(brand: str) -> str:
    """
    Return default brand if brand is empty.
    """
    if not brand or brand.strip() == "":
        return "سایر"
    return brand.strip()


def check_product_exists(name: str, brand: str) -> dict:
    """
    Check if product exists by name and brand.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute(
        "SELECT id, price, stock_quantity FROM products WHERE name = ? AND brand = ?",
        (name.strip(), brand.strip())
    )
    result = cur.fetchone()
    conn.close()
    
    return dict(result) if result else None


def add_or_update_product(name: str, brand: str, price: int, stock: int, description: str = "", image_path: str = "") -> dict:
    """
    Add new product or update existing product.
    
    For existing product:
        - Price is replaced with new price
        - Stock is added to existing stock
    """
    # اعتبارسنجی
    if not name or name.strip() == "":
        return {
            "success": False,
            "message": "❌ نام محصول نمی‌تواند خالی باشد"
        }
    
    name = name.strip()
    brand = get_default_brand(brand)
    price = validate_price(str(price))
    stock = validate_stock(str(stock))
    
    # بررسی وجود محصول
    existing = check_product_exists(name, brand)
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if existing:
        # به‌روزرسانی محصول موجود
        old_price = existing["price"]
        old_stock = existing["stock_quantity"]
        product_id = existing["id"]
        
        new_stock = old_stock + stock  # موجودی قبلی + موجودی جدید
        
        cur.execute("""
            UPDATE products 
            SET price = ?, stock_quantity = ?, description = ?, path_image = ?
            WHERE id = ?
        """, (price, new_stock, description, image_path, product_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "product_id": product_id,
            "is_new": False,
            "message": f"✅ محصول به‌روزرسانی شد",
            "old_stock": old_stock,
            "new_stock": new_stock,
            "added_stock": stock,
            "old_price": old_price,
            "new_price": price
        }
    else:
        # افزودن محصول جدید
        cur.execute("""
            INSERT INTO products (name, brand, description, price, stock_quantity, path_image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, brand, description, price, stock, image_path))
        
        product_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "product_id": product_id,
            "is_new": True,
            "message": f"✅ محصول جدید اضافه شد",
            "name": name,
            "brand": brand,
            "price": price,
            "stock": stock
        }


def add_product_from_dict(product_data: dict) -> dict:
    """
    Add product from dictionary (for Excel or single product).
    """
    return add_or_update_product(
        name=product_data.get("name", ""),
        brand=product_data.get("brand", ""),
        price=product_data.get("price", 0),
        stock=product_data.get("stock", 0),
        description=product_data.get("description", ""),
        image_path=product_data.get("image_path", "")
    )


def add_product_from_excel_row(row: dict) -> dict:
    """
    Add product from Excel row.
    """
    return add_or_update_product(
        name=row.get("name", ""),
        brand=row.get("brand", ""),
        price=row.get("price", 0),
        stock=row.get("stock", 0),
        description=row.get("desc", ""),
        image_path=""
    )