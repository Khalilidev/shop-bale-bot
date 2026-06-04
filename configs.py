# Insert the received token from @botfather in bale.

# Example TOKEN : 17106917:l7wGV-6e0GY7AZsfJl149vJR349eV. 
TOKEN = None # type : str

# After insert token, run this code. then copy the received id in chat and insert it to (Id):
"""
from bale import Bot, Message
bot = Bot(TOKEN)
@bot.event
async def on_message(message:Message):
    if message.text == "/start":
        await message.reply(message.chat.id)
bot.run()
"""
Id = None # type : int