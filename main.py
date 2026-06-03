from core.bot import bot
from databases.init import *
def main():
    init_db()
if __name__ == "__main__":
    main()
    bot.run()