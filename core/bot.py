from email import message
from bale import Bot, Message, CallbackQuery
from configs import TOKEN
from core.logging import is_seller
from keyboards.seller.account_book.main_menu_account_book import main_menu_account_book
from keyboards.seller.main_menu_seller import *
from texts.seller_texts import *
from callbacks.cb_main_menu_seller import *
bot = Bot(TOKEN)
@bot.event
async def on_message(message:Message):
    print(f"Message from {message.chat.id}")
    if message.text == '/start':
        if is_seller(message.chat.id):
            await message.reply(WELLCOME_SELLER_TXT, components=main_menu_seller())

@bot.event
async def on_callback(callback:CallbackQuery):
    if callback.data == CB_SELLER_ACCOUNT_BOOK:
        await callback.message.edit(ACCOUNT_BOOK_TXT, components=main_menu_account_book())
if __name__ == "__main__":
    bot.run()