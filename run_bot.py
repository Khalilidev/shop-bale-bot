# Run the bot from this file!
from core.bot import bot
from databases.init import *
from handlers.create_images_folder import create_images_folder
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
    IMAGES_FOLDER_PATH = create_images_folder()
    bot.run()