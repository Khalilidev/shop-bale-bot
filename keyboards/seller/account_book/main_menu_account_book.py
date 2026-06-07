from bale import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_seller_account_book import *
from callbacks.cb_main_menu_seller import CB_BACK_TO_MAIN_MENU_SELLER

def main_menu_account_book():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("➕ افزودن مشتری جدید", callback_data=CB_SELLER_ACCOUNT_BOOK_ADD_CUSTOMER)
    btn2 = InlineKeyboardButton("📊 افزایش/کاهش بدهی مشتری", callback_data=CB_SELLER_ACCOUNT_BOOK_EDIT_CUSTOMER)
    btn3 = InlineKeyboardButton("📄 دریافت PDF حساب ها", callback_data=CB_SELLER_ACCOUNT_BOOK_GET_PDF)
    btn4 = InlineKeyboardButton("🔙 بازگشت به منوی قبلی", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    return keyboard

def apply_customer():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("✅ ثبت اطلاعات", callback_data=CB_SELLER_ACCOUNT_BOOK_APPLY_CUSTOMER)
    btn2 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_ACCOUNT_BOOK)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)

    return keyboard

def back_btn():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_ACCOUNT_BOOK)

    keyboard.add(btn1, row=1)

    return keyboard

def debt_operation_buttons():
    keyboard = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("➕ افزایش بدهی", callback_data=CB_SELLER_ACCOUNT_BOOK_INCREASE_DEBT)
    btn2 = InlineKeyboardButton("➖ کاهش بدهی", callback_data=CB_SELLER_ACCOUNT_BOOK_DECREASE_DEBT)
    btn3 = InlineKeyboardButton("🔙 بازگشت", callback_data=CB_SELLER_ACCOUNT_BOOK)

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)

    return keyboard

def confirm_debt_buttons():
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("✅ تأیید و ثبت", callback_data=CB_SELLER_ACCOUNT_BOOK_CONFIRM_DEBT)
    btn2 = InlineKeyboardButton("🔙 انصراف", callback_data=CB_SELLER_ACCOUNT_BOOK)
    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    return keyboard