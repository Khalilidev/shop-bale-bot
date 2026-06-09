from bale import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.cb_seller_products_managment import *
from callbacks.cb_main_menu_seller import *

def main_menu_products_managment():
    """
    Create the keyboard for products managment.

    Args:
        None
    Returns:
        (InlineKeyboardMarkup): keyboard with created btns.
    """
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("📊 افزودن محصول با Excel", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_ADD_ECXEL)
    btn2 = InlineKeyboardButton("➕ افزودن تک محصول", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_ADD_PRODUCT)
    btn3 = InlineKeyboardButton("📋 لیست همه محصولات", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_PRODUCTS_LIST)
    btn4 = InlineKeyboardButton("✏️ ویرایش محصول", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_PRODUCT_EDIT)
    btn6 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn6, row=6)

    return keyboard

def back_products_managment_menu():
    """
    Create back btn for back to products managment menu.
    
    Args:
        None
    Returns:
        keyboard(InlineKeyboardMarkup):
            A keyboard with 1 btn.
    """
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_PRODUCTS_MANAGMENT)

    keyboard.add(btn1, row=1)

    return keyboard

def apply_products():
    """
    Create a keyboard for applying entered product with the received back btn.
    Args:
        None
    Returns:
        keyboard(InlineKeyboardMarkup): A keyboard with back & apply btns.
    """
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_PRODUCTS_MANAGMENT)
    btn2 = InlineKeyboardButton("✅ ثبت اطلاعات محصول", callback_data=CB_SELLER_APPLY_PRODUCTS)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)

    return keyboard

def edit_product_back_keyboard():
    """"
    Keyboard return while editing product
    Args:
        None
    Returns:
        InlineKeyboardMarkup: A keyboard returns you to the product menu.
    """
    keyboard = InlineKeyboardMarkup()

    btn_back = InlineKeyboardButton("🔙 بازگشت به منوی محصول", callback_data=CB_SELLER_PRODUCT_BACK_TO_MENU)

    keyboard.add(btn_back, row=1)
    return keyboard