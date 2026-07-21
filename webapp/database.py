"""
Database connection and operations for web app.
"""
import sqlite3
import os
from typing import List, Dict, Optional

DB_NAME = "database.db"

def get_db_connection():
    """
    Create a connection to the database.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_products() -> List[Dict]:
    """
    Get all products from database.
    
    Returns:
        List[Dict]: List of all products
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            name,
            brand,
            category,
            description,
            price,
            stock_quantity as stock,
            path_image
        FROM products
        WHERE stock_quantity > 0
        ORDER BY category, name
    """)
    
    products = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    # Fix image paths
    for product in products:
        if product.get('path_image'):
            # Convert relative path to URL path
            image_path = product['path_image']
            if os.path.exists(image_path):
                product['image_url'] = f"/images/{os.path.basename(image_path)}"
            else:
                product['image_url'] = None
        else:
            product['image_url'] = None
    
    return products

def get_products_by_category(category: str) -> List[Dict]:
    """
    Get products by category.
    
    Args:
        category: Category name
    
    Returns:
        List[Dict]: List of products in category
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            name,
            brand,
            category,
            description,
            price,
            stock_quantity as stock,
            path_image
        FROM products
        WHERE category = ? AND stock_quantity > 0
        ORDER BY name
    """, (category,))
    
    products = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    for product in products:
        if product.get('path_image') and os.path.exists(product['path_image']):
            product['image_url'] = f"/images/{os.path.basename(product['path_image'])}"
        else:
            product['image_url'] = None
    
    return products

def get_categories() -> List[str]:
    """
    Get all unique categories from products.
    
    Returns:
        List[str]: List of categories with products
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT DISTINCT category 
        FROM products 
        WHERE stock_quantity > 0
        ORDER BY category
    """)
    
    categories = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    
    return categories

def update_product_stock(product_id: int, quantity: int) -> bool:
    """
    Update product stock quantity.
    
    Args:
        product_id: Product ID
        quantity: Quantity to subtract
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE products 
            SET stock_quantity = stock_quantity - ? 
            WHERE id = ? AND stock_quantity >= ?
        """, (quantity, product_id, quantity))
        
        if cur.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    except Exception as e:
        print(f"Error updating stock: {e}")
        conn.close()
        return False

def get_product(product_id: int) -> Optional[Dict]:
    """
    Get a single product by ID.
    
    Args:
        product_id: Product ID
    
    Returns:
        Optional[Dict]: Product data or None
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            name,
            brand,
            category,
            description,
            price,
            stock_quantity as stock,
            path_image
        FROM products
        WHERE id = ?
    """, (product_id,))
    
    product = cur.fetchone()
    conn.close()
    
    if product:
        product = dict(product)
        if product.get('path_image') and os.path.exists(product['path_image']):
            product['image_url'] = f"/images/{os.path.basename(product['path_image'])}"
        else:
            product['image_url'] = None
        return product
    
    return None
def save_order(user_id: int, customer_name: str, customer_phone: str, items: List[Dict], total_price: int) -> Optional[int]:
    """ذخیره سفارش جدید در دیتابیس"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # ثبت رکورد اصلی سفارش
        cur.execute("""
            INSERT INTO orders (user_id, customer_name, customer_phone, total_price, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (user_id, customer_name, customer_phone, total_price))
        
        order_id = cur.lastrowid
        
        # ثبت اقلام سفارش
        for item in items:
            product = get_product(item['product_id'])
            if product:
                cur.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, item['product_id'], item['quantity'], product['price']))
        
        conn.commit()
        return order_id
    except Exception as e:
        print(f"Database error saving order: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()