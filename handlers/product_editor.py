"""
Handler for editing and deleting products
"""
import sqlite3
import os
from datetime import datetime
from bale import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.cb_seller_products_managment import *
from texts.seller_texts import *
from handlers.categories import CATEGORIES

DB_NAME = "database.db"

def get_product_by_id(product_id: int) -> dict:
    """
    Get product by ID
    
    Args:
        product_id: Product ID
        
    Returns:
        dict: Product data or None if not found
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, brand, category, description, price, stock_quantity as stock, path_image
        FROM products 
        WHERE id = ?
    """, (product_id,))
    
    product = cur.fetchone()
    conn.close()
    
    return dict(product) if product else None

def update_product_field(product_id: int, field: str, value) -> bool:
    """
    Update a specific field of a product
    
    Args:
        product_id: Product ID
        field: Field name (name, brand, category, price, stock, description, path_image)
        value: New value
        
    Returns:
        bool: True if successful, False otherwise
    """
    if field == "category" and value not in CATEGORIES:
        value = "بدون دسته‌بندی"
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    try:
        query = f"UPDATE products SET {field} = ? WHERE id = ?"
        cur.execute(query, (value, product_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating product: {e}")
        conn.close()
        return False

def delete_product(product_id: int) -> bool:
    """
    Delete a product from database.
    
    Args:
        product_id: Product ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT path_image FROM products WHERE id = ?", (product_id,))
        result = cur.fetchone()
        if result and result[0] and os.path.exists(result[0]):
            os.remove(result[0])
        
        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting product: {e}")
        conn.close()
        return False

def format_product_info(product: dict) -> str:
    """
    Format product information for display.
    
    Args:
        product: Product dictionary
    
    Returns:
        str: Formatted product info
    """
    has_image = "✅ دارد" if product.get("path_image") and os.path.exists(product.get("path_image", "")) else "❌ ندارد"
    category = product.get('category', 'بدون دسته‌بندی')
    
    info = (
        f"📦 **اطلاعات محصول**\n\n"
        f"🆔 **شناسه:** {product['id']}\n"
        f"📝 **نام:** {product['name']}\n"
        f"🏷️ **برند:** {product['brand']}\n"
        f"📂 **دسته‌بندی:** {category}\n"
        f"💰 **قیمت:** {product['price']:,} تومان\n"
        f"📦 **موجودی:** {product['stock']} عدد\n"
        f"📸 **عکس:** {has_image}\n")
    
    if product.get('description'):
        info += f"📝 **توضیحات:** {product['description'][:200]}"
        if len(product['description']) > 200:
            info += "..."
    
    return info

def get_product_edit_keyboard(product_id: int, has_image: bool) -> InlineKeyboardMarkup:
    """
    Create keyboard for product edit menu.
    
    Args:
        product_id: Product ID
        has_image: Whether product has image
    
    Returns:
        InlineKeyboardMarkup: Keyboard with edit options
    """
    keyboard = InlineKeyboardMarkup()
    
    btn1 = InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"{CB_SELLER_PRODUCT_EDIT_NAME}:{product_id}")
    btn2 = InlineKeyboardButton("🏷️ ویرایش برند", callback_data=f"{CB_SELLER_PRODUCT_EDIT_BRAND}:{product_id}")
    btn3 = InlineKeyboardButton("📂 ویرایش دسته‌بندی", callback_data=f"{CB_SELLER_PRODUCT_EDIT_CATEGORY}:{product_id}")
    btn4 = InlineKeyboardButton("💰 ویرایش قیمت", callback_data=f"{CB_SELLER_PRODUCT_EDIT_PRICE}:{product_id}")
    btn5 = InlineKeyboardButton("📦 ویرایش موجودی", callback_data=f"{CB_SELLER_PRODUCT_EDIT_STOCK}:{product_id}")
    btn6 = InlineKeyboardButton("📝 ویرایش توضیحات", callback_data=f"{CB_SELLER_PRODUCT_EDIT_DESCRIPTION}:{product_id}")

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=5)
    keyboard.add(btn6, row=6)
    
    if has_image:
        btn7 = InlineKeyboardButton("🖼️ تغییر عکس", callback_data=f"{CB_SELLER_PRODUCT_EDIT_IMAGE}:{product_id}")
    else:
        btn7 = InlineKeyboardButton("➕ افزودن عکس", callback_data=f"{CB_SELLER_PRODUCT_EDIT_IMAGE}:{product_id}")
    
    keyboard.add(btn7, row=7)
    btn8 = InlineKeyboardButton("🗑️ حذف محصول", callback_data=f"{CB_SELLER_PRODUCT_DELETE}:{product_id}")
    btn9 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_PRODUCT_BACK_TO_MENU)
    keyboard.add(btn8, row=8)
    keyboard.add(btn9, row=9)
    
    return keyboard

def get_delete_confirmation_keyboard(product_id: int, product_name: str) -> InlineKeyboardMarkup:
    """
    Create keyboard for delete confirmation.
    
    Args:
        product_id: Product ID
        product_name: Product name for display
    
    Returns:
        InlineKeyboardMarkup: Keyboard with confirm/cancel buttons
    """
    keyboard = InlineKeyboardMarkup()
    
    btn1 = InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"{CB_SELLER_PRODUCT_DELETE_CONFIRM}:{product_id}")
    btn2 = InlineKeyboardButton("❌ انصراف", callback_data=CB_SELLER_PRODUCT_BACK_TO_MENU)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    
    return keyboard

def save_product_image(product_id: int, file_content: bytes, product_name: str) -> str:
    """
    Save product image and update database.
    
    Args:
        product_id: Product ID
        file_content: Image file content
        product_name: Product name for filename
    
    Returns:
        str: Saved image path or empty string if failed
    """
    try:
        safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{product_id}_{timestamp}.jpg"
        
        IMAGES_FOLDER = "products_images"
        if not os.path.exists(IMAGES_FOLDER):
            os.makedirs(IMAGES_FOLDER)
        
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT path_image FROM products WHERE id = ?", (product_id,))
        old_image = cur.fetchone()
        if old_image and old_image[0] and os.path.exists(old_image[0]):
            os.remove(old_image[0])
        
        cur.execute("UPDATE products SET path_image = ? WHERE id = ?", (filepath, product_id))
        conn.commit()
        conn.close()
        
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return ""