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
    if is_seller(message.chat.id) and message.chat.id in user_state:
        if user_state[message.chat.id] == "waiting_for_name":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["name"] = message.text
            user_state[message.chat.id] = "waiting_for_phone"
            await message.reply(
                f"{CUSTOMER_NAME_RECEIVED_TEXT.format(name=message.text)}\n\n{ASK_CUSTOMER_PHONE_TEXT}",components=back_btn())
            return
        
        elif user_state[message.chat.id] == "waiting_for_phone":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["phone"] = message.text
            user_state[message.chat.id] = "waiting_for_amount"
            await message.reply(
                f"{CUSTOMER_PHONE_RECEIVED_TEXT.format(phone=message.text)}\n\n{ASK_CUSTOMER_DEBT_TEXT}",components=back_btn())
            return 
        
        elif user_state[message.chat.id] == "waiting_for_amount":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["amount"] = message.text
            user_state[message.chat.id] = "waiting_for_reason"
            await message.reply(
                f"{CUSTOMER_DEBT_RECEIVED_TEXT.format(amount=message.text)}\n\n{ASK_CUSTOMER_REASON_TEXT}",components=back_btn())
            return 
        
        elif user_state[message.chat.id] == "waiting_for_reason":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["reason"] = message.text
            user_state[message.chat.id] = "waiting_for_confirmation"
            await message.reply(
                CUSTOMER_INFO_CONFIRM_TEXT.format(
                    name=temp_customer[message.chat.id]["name"],
                    phone=temp_customer[message.chat.id]["phone"],
                    amount=temp_customer[message.chat.id]["amount"],
                    reason=temp_customer[message.chat.id]["reason"]),components=apply_customer())
            return
        
    if message.text == '/start':
        if is_seller(message.chat.id):
            await message.reply(WELCOME_SELLER_TEXT, components=main_menu_seller())

@bot.event
async def on_callback(callback: CallbackQuery):
    if callback.data == CB_SELLER_ACCOUNT_BOOK:
        await callback.message.edit(ACCOUNT_BOOK_TEXT, components=main_menu_account_book())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_ADD_CUSTOMER:
        user_state[callback.message.chat.id] = "waiting_for_name"
        temp_customer[callback.message.chat.id] = {}
        await callback.message.edit(ASK_CUSTOMER_NAME_TEXT, components=back_btn())

    # elif callback.data == CB_SELLER_ACCOUNT_BOOK_APPLY_CUSTOMER:

if __name__ == "__main__":
    bot.run()