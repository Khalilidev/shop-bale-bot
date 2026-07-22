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
    به روزرسانی موجودی محصول - این تابع دیگر استفاده نمی‌شود
    اما برای سازگاری نگه داشته شده است
    
    Args:
        product_id: Product ID
        quantity: Quantity to subtract
    
    Returns:
        bool: True if successful, False otherwise
    """
    # این تابع دیگر استفاده نمی‌شود
    return True

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

def save_order(customer_name: str, customer_phone: str, customer_address: Optional[str] = None, customer_note: Optional[str] = None, items: List[Dict] = None, total_price: int = 0) -> Optional[int]:
    """
    save oeder in database
    Args:
        customer_name: customer name
        customer_phone: customer phone
        customer_address: customer address
        customer_note: customer notes
        items: list 
        total_price: total price
    Returns:
        Optional[int]: None
    """
    if items is None:
        items = []
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO orders (
                customer_name, 
                customer_phone, 
                customer_address,
                customer_note,
                total_price, 
                status
            )
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (customer_name, customer_phone, customer_address, customer_note, total_price))
        
        order_id = cur.lastrowid
        
        for item in items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item['product_id'], item['quantity'], item.get('price', 0)))
        
        conn.commit()
        return order_id
    except Exception as e:
        print(f"Database error saving order: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()