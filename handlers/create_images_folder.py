"""
Handler for creating images folder at startup.
"""
import os
def create_images_folder():
    """
    Create a folder for storing product images if it doesn't exist.
    
    Args:
        None
    
    Returns:
        str: Path to the images folder
    """
    IMAGES_FOLDER = "products_images"
    folder_path = os.path.join(os.getcwd(), IMAGES_FOLDER)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f" Images folder created: {folder_path}")
    else:
        print(f"Images folder already exists: {folder_path}")
    return folder_path