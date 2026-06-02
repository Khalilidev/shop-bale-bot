from bale import Bot, Message
from configs import TOKEN
from core.logging import is_seller
from keyboards.main_menu_seller import *
bot = Bot(TOKEN)
@bot.event
async def on_message(message:Message):
    print(f"Message from {message.chat.id}")
    if message.text == '/start':
        if is_seller(message.chat.id):
            await message.reply("👋 **سلام فروشنده عزیز**\n\nبه پنل مدیریت خوش آمدید. از طریق منوی زیر می‌توانید فروشگاه خود را مدیریت کنید:",
                                components=main_menu_seller())

if __name__ == "__main__":
    bot.run()