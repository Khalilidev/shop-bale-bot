from bale import Bot, Message
from configs import TOKEN
from core.logging import is_seller
bot = Bot(TOKEN)
@bot.event
async def on_message(message:Message):
    print(f"Message from {message.chat.id}")
    if message.text == '/start':
        if is_seller(message.chat.id):
            await message.reply("سلام به بخش فروشنده خوش اومدی")
if __name__ == "__main__":
    bot.run()