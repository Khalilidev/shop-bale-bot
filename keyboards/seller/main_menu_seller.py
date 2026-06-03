from bale import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_main_menu_seller import *
def main_menu_seller():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("دفتر حساب", callback_data=CB_S_ACCOUNT_BOOK)

    keyboard.add(btn1, row=1)
    
    return keyboard