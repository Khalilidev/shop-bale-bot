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
    btn4 = InlineKeyboardButton("💰 تغییر قیمت محصولات", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_PRICE_CHANGE)
    btn5 = InlineKeyboardButton("🎁 اعمال تخفیف موقت", callback_data=CB_SELLER_PRODUCTS_MANAGMENT_APPLY_DISCOUNT)
    btn6 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=5)
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