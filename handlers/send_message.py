import asyncio
import sqlite3
from bale import Bot
DB_NAME = "database.db"
async def send_message_to_customers(bot:Bot, text:str):
    """
    send message to all users.
    Args:
        bot(Bot):
            (bot = Bot(TOKEN))
        text(str):
            Text message.
    Returns:
        None
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn .close()
    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(user_id, text=text)
            await asyncio.sleep(0.05)
            print(f"message seccessfully sent to : {user_id}")
        except:
            print(f"message was not sent to {user_id}")