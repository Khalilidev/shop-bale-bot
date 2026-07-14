from bale import InlineKeyboardButton, InlineKeyboardMarkup

class WebAppInfo:
    def __init__(self, url):
        self.url = f"https://ble.ir/shop_testbot?startapp={url}"
        
def main_menu_customer():
    keyboard = InlineKeyboardMarkup()
    web_app_url = WebAppInfo(url='https://docs.bale.ai/miniapp')
    btn1 = InlineKeyboardButton('نمایش محصولات', url=web_app_url.url)
    btn2 = InlineKeyboardButton('دریافت PDF محصولات')
    btn3 = InlineKeyboardButton('سبد خرید')
    btn4 = InlineKeyboardButton('بدهی شما به فروشگاه')
    btn5 = InlineKeyboardButton('راه ارتباطی')

    keyboard.add(btn1, row=1)
    keyboard.add(btn2, row=2)
    keyboard.add(btn3, row=3)
    keyboard.add(btn4, row=4)
    keyboard.add(btn5, row=5)
    
    return keyboard
