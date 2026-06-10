from bale import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_seller_send_message import CB_BROADCAST_CONFIRM
from callbacks.cb_main_menu_seller import CB_BACK_TO_MAIN_MENU_SELLER
from cv2 import add
def broadcast_confirm_keyboard():
    """
    confirm or cancle send messsage keyborad.
    Args:
        None
    Returns:
        (InlineKeyboardMarkup):
            a keyboard with two btns.
    """
    keyboard = InlineKeyboardMarkup()
    
    btn_confirm = InlineKeyboardButton("✅ بله، ارسال شود", callback_data=CB_BROADCAST_CONFIRM)
    btn_cancel = InlineKeyboardButton("🔙 لغو و بازگشت", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)
    
    keyboard.add(btn_confirm, row=1)
    keyboard.add(btn_cancel, row=2)
    
    return keyboard

def back_to_main_menu_seller():
    keyboard = InlineKeyboardMarkup()

    btn = InlineKeyboardButton("🔙 بازگشت به منوی قبلی", callback_data=CB_BACK_TO_MAIN_MENU_SELLER)

    keyboard.add(btn, row=1)

    return keyboard
