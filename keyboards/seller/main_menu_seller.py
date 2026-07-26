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

    btn1 = InlineKeyboardButton("گزارشات", callback_data=CB_SELLER_REPORTS)
    btn2 = InlineKeyboardButton("مدیریت محصولات", callback_data=CB_SELLER_PRODUCTS_MANAGMENT)
    btn3 = InlineKeyboardButton("دفتر حساب", callback_data=CB_SELLER_ACCOUNT_BOOK)
    btn4 = InlineKeyboardButton("ارسال پیام به مشتریان", callback_data=CB_SELLER_SEND_MESSAGE)
    btn5 = InlineKeyboardButton("ویرایش راه ارتباطی", callback_data=CB_EDIT_CONTACT)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=5)
    
    return keyboard