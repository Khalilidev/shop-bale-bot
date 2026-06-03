from bale import Bot, Message, CallbackQuery
from configs import TOKEN
from core.logging import is_seller
from keyboards.seller.account_book.main_menu_account_book import *
from keyboards.seller.main_menu_seller import *
from texts.seller_texts import *
from callbacks.cb_main_menu_seller import *
from callbacks.cb_seller_account_book import *

user_state = {}
temp_customer = {}

bot = Bot(TOKEN)

@bot.event
async def on_message(message: Message):
    print(f"Message from {message.chat.id}")
    
    # دریافت نام
    if is_seller(message.chat.id) and message.chat.id in user_state:
        if user_state[message.chat.id] == "waiting_for_name":
            if message.chat.id not in temp_customer: temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["name"] = message.text
            user_state[message.chat.id] = "waiting_for_phone"
            await message.reply(f"✅ نام *{message.text}* ثبت شد.\n📱 حالا شماره تماس رو وارد کن:", components=back_btn())
            return
        
        elif user_state[message.chat.id] == "waiting_for_phone":
            if message.chat.id not in temp_customer: temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["phone"] = message.text
            user_state[message.chat.id] = "waiting_for_amount"
            await message.reply(f"شماره تماس *{message.text}* وارد شد!\nحال بدهی مشتری را وارد کنید.به عنوان مثال 5000\n(مبلغ را به تومان وارد کنید)", components=back_btn())
            return 
        
        elif user_state[message.chat.id] == "waiting_for_amount":
            temp_customer[message.chat.id]["amount"] = message.text
            user_state[message.chat.id] = None
            await message.reply(f"اطلاعات وارد شده : \nنام : {temp_customer[message.chat.id]["name"]}\nشماره تماس : {temp_customer[message.chat.id]["phone"]}\nبدهی : {temp_customer[message.chat.id]["amount"]}\nآیا قصد ثبت اطالاعات بالا را دارید ؟ ", components=aplly_customer())
            return 
    if message.text == '/start':
        if is_seller(message.chat.id):
            await message.reply(WELLCOME_SELLER_TXT, components=main_menu_seller())

@bot.event
async def on_callback(callback: CallbackQuery):
    
    if callback.data == CB_SELLER_ACCOUNT_BOOK:
        await callback.message.edit(ACCOUNT_BOOK_TXT, components=main_menu_account_book())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_ADD_CUSTOMER:
        user_state[callback.message.chat.id] = "waiting_for_name"
        temp_customer[callback.message.chat.id] = {}
        await callback.message.edit("➕ لطفا نام مشتری را وارد کنید:", components=back_btn())

if __name__ == "__main__":
    bot.run()