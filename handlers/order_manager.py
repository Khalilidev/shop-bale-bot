from bale import Bot, Message, CallbackQuery
from callbacks.cb_seller_reports import *
async def order_manager(callback:CallbackQuery):
    if callback.data.startswith("seller:reports:new_orders:"):
        if callback.data == CB_SELLER_REPORTS_NEW_ORDERS_NEXT:
            pass
        elif callback.data == CB_SELLER_REPORTS_NEW_ORDERS_PREV:
            pass
        elif callback.data == CB_SELLER_REPORTS_NEW_ORDERS_CONFIRTM_ORDER:
            pass
        elif callback.data == CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER:
            pass
        
    elif callback.data == CB_SELLER_REPORTS_CONFIRMED_ORDERS:
        pass
    elif callback.data == CB_SELLER_REPORTS_CANCELLED_ORDERS:
        pass
    elif callback.data == CB_SELLER_REPORTS_SHOW_DETAILS:
        pass