"""
Configuration file.

Sensitive information is loaded from environment variables.

For local development:
1. Create a file named ".env" in the project root.
2. Add the following variables:

TOKEN=your_bot_token
SELLER_ID=your_seller_id
BOT_USERNAME=your_bot_username

The .env file should NOT be committed to Git.
"""

import os
from dotenv import load_dotenv

# Load variables from .env (if it exists)
load_dotenv()

# ==========================================================
# How to get your Seller ID
# ==========================================================
#
# 1. Insert your bot TOKEN into the code below.
# 2. Run the script.
# 3. Send /start to your bot in Bale.
# 4. The bot will reply with your numeric chat ID.
# 5. Put that value into SELLER_ID inside your .env file.
#
# Example:
#
# from bale import Bot, Message
#
# bot = Bot(TOKEN)
#
# @bot.event
# async def on_message(message: Message):
#     if message.text == "/start":
#         await message.reply(message.chat.id)
#
# bot.run()
# ==========================================================

# Bot Token
TOKEN = os.environ["TOKEN"]

# Seller ID
SELLER_ID = int(os.environ["SELLER_ID"])