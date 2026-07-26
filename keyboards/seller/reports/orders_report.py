from bale import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_main_menu_seller import CB_BACK_TO_MAIN_MENU_SELLER
from callbacks.cb_seller_reports import *

def main_menu_orders_report():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("سفارش های جدید🆕", callback_data=CB_SELLER_REPORTS_NEW_ORDERS)
    btn2 = InlineKeyboardButton("سفارش های تایید شده✅", callback_data=CB_SELLER_REPORTS_CONFIRMED_ORDERS)
    btn3 = InlineKeyboardButton("سفارش های لغو شده❌", callback_data=CB_SELLER_REPORTS_CANCELLED_ORDERS)
    btn4 = InlineKeyboardButton(" بازگشت📋", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)

    return keyboard

def new_orders():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("دیدن جزئیات سفارش ", callback_data=CB_SELLER_REPORTS_SHOW_DETAILS)
    btn2 = InlineKeyboardButton("ثبت سفارش", callback_data=CB_SELLER_REPORTS_NEW_ORDERS_CONFIRTM_ORDER)
    btn3 = InlineKeyboardButton("لغو کردن سفارش", callback_data=CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER)
    btn4 = InlineKeyboardButton("قبلی", callback_data=CB_SELLER_REPORTS_NEW_ORDERS_PREV)
    btn5 = InlineKeyboardButton("بعدی", callback_data=CB_SELLER_REPORTS_NEW_ORDERS_NEXT)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=4)

    return keyboard
