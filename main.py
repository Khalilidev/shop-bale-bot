# Run the bot from this file!
from core.bot import bot
from databases.init import *
def main():
    """
    Create the database with call init_db.
    Args:
        None
    Returns:
        None
    """
    init_db()
if __name__ == "__main__":
    """
    Call the main and run bot.
    """
    main()
    bot.run()