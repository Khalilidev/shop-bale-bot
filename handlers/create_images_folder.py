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
    # نام پوشه برای ذخیره عکس‌ها
    IMAGES_FOLDER = "products_images"
    
    # مسیر کامل پوشه در پروژه
    folder_path = os.path.join(os.getcwd(), IMAGES_FOLDER)
    # اگر پوشه وجود نداشت، آن را ایجاد کن
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f" Images folder created: {folder_path}")
    else:
        print(f"Images folder already exists: {folder_path}")
    return folder_path