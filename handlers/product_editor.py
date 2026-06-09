import sqlite3
import os
from datetime import datetime
from bale import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.seller.products_managment.prodocts_managment_keyboards import back_products_managment_menu
DB_NAME = "database.db"
def get_product_by_id(product_id: int) -> dict:
    """
    Get product details from database by ID.
    
    Args:
        product_id: Product ID
    
    Returns:
        dict: Product details or None if not found
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            name,
            brand,
            description,
            price,
            stock_quantity as stock,
            path_image
        FROM products
        WHERE id = ?
                    """, (product_id,))
    
    result = cur.fetchone()
    conn.close()
    
    return dict(result) if result else None

def update_product_field(product_id: int, field: str, value) -> bool:
    """
    Update a specific field of a product.
    
    Args:
        product_id: Product ID
        field: Field name (name, brand, price, stock_quantity, description, path_image)
        value: New value
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    try:
        cur.execute(f"UPDATE products SET {field} = ? WHERE id = ?", (value, product_id))
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
        # Delete product from database
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
    
    info = (
        f"📦 **اطلاعات محصول**\n\n"
        f"🆔 **شناسه:** {product['id']}\n"
        f"📝 **نام:** {product['name']}\n"
        f"🏷️ **برند:** {product['brand']}\n"
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
    from callbacks.cb_seller_products_managment import (
        CB_SELLER_PRODUCT_EDIT_NAME,
        CB_SELLER_PRODUCT_EDIT_BRAND,
        CB_SELLER_PRODUCT_EDIT_PRICE,
        CB_SELLER_PRODUCT_EDIT_STOCK,
        CB_SELLER_PRODUCT_EDIT_DESCRIPTION,
        CB_SELLER_PRODUCT_EDIT_IMAGE,
        CB_SELLER_PRODUCT_DELETE,
        CB_SELLER_PRODUCT_BACK_TO_MENU)
    
    keyboard = InlineKeyboardMarkup()
    
    btn1 = InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"{CB_SELLER_PRODUCT_EDIT_NAME}:{product_id}")
    btn2 = InlineKeyboardButton("🏷️ ویرایش برند", callback_data=f"{CB_SELLER_PRODUCT_EDIT_BRAND}:{product_id}")
    btn3 = InlineKeyboardButton("💰 ویرایش قیمت", callback_data=f"{CB_SELLER_PRODUCT_EDIT_PRICE}:{product_id}")
    btn4 = InlineKeyboardButton("📦 ویرایش موجودی", callback_data=f"{CB_SELLER_PRODUCT_EDIT_STOCK}:{product_id}")
    btn5 = InlineKeyboardButton("📝 ویرایش توضیحات", callback_data=f"{CB_SELLER_PRODUCT_EDIT_DESCRIPTION}:{product_id}")

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=5)
    
    if has_image:
        btn6 = InlineKeyboardButton("🖼️ تغییر عکس", callback_data=f"{CB_SELLER_PRODUCT_EDIT_IMAGE}:{product_id}")
        keyboard.add(btn6, row=6)
    else:
        btn6 = InlineKeyboardButton("➕ افزودن عکس", callback_data=f"{CB_SELLER_PRODUCT_EDIT_IMAGE}:{product_id}")
        keyboard.add(btn6, row=6)
    btn7 = InlineKeyboardButton("🗑️ حذف محصول", callback_data=f"{CB_SELLER_PRODUCT_DELETE}:{product_id}")
    btn8 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_PRODUCT_BACK_TO_MENU)
    keyboard.add(btn7, row=7)
    keyboard.add(btn8, row=8)
    
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
    from callbacks.cb_seller_products_managment import CB_SELLER_PRODUCT_DELETE_CONFIRM, CB_SELLER_PRODUCT_BACK_TO_MENU
    
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
        
        # Remove old image if exists.
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT path_image FROM products WHERE id = ?", (product_id,))
        old_image = cur.fetchone()
        if old_image and old_image[0] and os.path.exists(old_image[0]):
            os.remove(old_image[0])
        
        # updata image path in database.
        cur.execute("UPDATE products SET path_image = ? WHERE id = ?", (filepath, product_id))
        conn.commit()
        conn.close()
        
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return ""