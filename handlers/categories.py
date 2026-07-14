CATEGORIES = [
    "قطعات پلاستیکی",
    "قطعات آهنی",
    "آلومینیومی",
    "قطعات برقی و مسی",
    "انواع واشر",
    "قطعات لاستیکی",
    "پیچ و مهره",
    "بلبرینگ و بوش",
    "روغن موتور"
]

def get_categories():
    """
    Get list of categories.
    Returns:
        list: a list of categoris
    """
    return CATEGORIES

def get_category_keyboard(callback_prefix: str = None):
    """
   create a keyboard for categories
    
    Args:
        callback_prefix: prefix for callback data
    
    Returns:
        InlineKeyboardMarkup: categories keyborad
    """
    from bale import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup()
    buttons_per_row = 3
    
    for i, category in enumerate(CATEGORIES):
        row = i // buttons_per_row + 1
        callback_data = f"{callback_prefix}:{category}" if callback_prefix else category
        btn = InlineKeyboardButton(category, callback_data=callback_data)
        keyboard.add(btn, row=row)
    
    return keyboard

def get_category_buttons():
    """
    Get keyborad for categories.
    Returns:
        list: list of categories.
    """
    return [[cat] for cat in CATEGORIES]

def get_category_by_index(index: int) -> str:
    """
    Get name of categori by index.
    Args:
        index: index of categoies.
    
    Returns:
        str: Name of category.
    """
    if 0 <= index < len(CATEGORIES):
        return CATEGORIES[index]
    return None

def get_category_display(category: str) -> str:
    """
    Get good display for category.
    """
    if category and category in CATEGORIES:
        return category
    return "بدون دسته‌بندی"