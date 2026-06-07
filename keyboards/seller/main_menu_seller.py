from bale import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_main_menu_seller import *
def main_menu_seller():
    """
    Create the keyboard for seller in first menu.

    Args:
        None.
    Returns:
        keyboard(InlineKeyboardMarkup):
            Created the keyboard with added btns.
    """
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("مدیریت محصولات", callback_data=CB_SELLER_PRODUCTS_MANAGMENT)
    btn2 = InlineKeyboardButton("دفتر حساب", callback_data=CB_SELLER_ACCOUNT_BOOK)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)

    return keyboard