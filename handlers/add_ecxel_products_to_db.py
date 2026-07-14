"""
Handler for processing Excel/CSV files and adding products to database.
"""
import pandas as pd
import os
from handlers.add_product_to_db import add_or_update_product, convert_persian_to_english
from handlers.categories import CATEGORIES

def process_excel_file(file_path: str) -> dict:
    """
    Process Excel/CSV file and add all products to database.
    
    Expected columns: name, brand, category, price, stock, desc
    
    Args:
        file_path: Path to Excel or CSV file
        
    Returns:
        dict: {
            "success": bool,
            "total_rows": int,
            "new_count": int,
            "updated_count": int,
            "error_count": int,
            "errors": list,
            "message": str
        }
    """
    results = {
        "success": True,
        "total_rows": 0,
        "new_count": 0,
        "updated_count": 0,
        "error_count": 0,
        "errors": [],
        "message": ""
    }
    
    try:
        # خواندن فایل
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)
        
        # بررسی وجود ستون‌های لازم
        required_columns = ['name', 'brand', 'price', 'stock']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            results["success"] = False
            results["message"] = f"❌ ستون‌های {missing_columns} در فایل وجود ندارند."
            return results
        
        results["total_rows"] = len(df)
        
        # پردازش هر سطر
        for index, row in df.iterrows():
            try:
                # دریافت و تمیز کردن داده‌ها
                name = str(row.get('name', '')).strip()
                brand = str(row.get('brand', '')).strip()
                category = str(row.get('category', '')).strip()
                
                # بررسی اینکه دسته‌بندی وارد شده در لیست دسته‌بندی‌ها وجود داشته باشد
                if category and category not in CATEGORIES:
                    # اگر دسته‌بندی معتبر نبود، "بدون دسته‌بندی" استفاده می‌شود
                    category = "بدون دسته‌بندی"
                
                price_str = str(row.get('price', '0'))
                stock_str = str(row.get('stock', '0'))
                description = str(row.get('desc', '')) if pd.notna(row.get('desc')) else ""
                
                # تبدیل اعداد فارسی به انگلیسی
                price_str = convert_persian_to_english(price_str)
                stock_str = convert_persian_to_english(stock_str)
                
                # حذف کاما و فاصله
                price_str = price_str.replace(',', '').replace(' ', '')
                stock_str = stock_str.replace(',', '').replace(' ', '')
                
                price = int(float(price_str)) if price_str else 0
                stock = int(float(stock_str)) if stock_str else 0
                
                # ذخیره در دیتابیس
                result = add_or_update_product(
                    name=name,
                    brand=brand,
                    price=price,
                    stock=stock,
                    category=category,
                    description=description,
                    image_path=""
                )
                
                if result["success"]:
                    if result["is_new"]:
                        results["new_count"] += 1
                    else:
                        results["updated_count"] += 1
                else:
                    results["error_count"] += 1
                    results["errors"].append(f"سطر {index + 2}: {result['message']}")
                    
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append(f"سطر {index + 2}: خطا - {str(e)}")
        
        # ساخت پیام نهایی
        results["message"] = (
            f"✅ **پردازش فایل با موفقیت انجام شد**\n\n"
            f"📊 **آمار نهایی:**\n"
            f"• کل ردیف‌ها: {results['total_rows']}\n"
            f"• محصولات جدید: {results['new_count']}\n"
            f"• محصولات به‌روزرسانی شده: {results['updated_count']}\n"
            f"• خطاها: {results['error_count']}"
        )
        
        if results["errors"] and len(results["errors"]) <= 5:
            results["message"] += f"\n\n❌ **خطاها:**\n" + "\n".join(results["errors"])
        
    except Exception as e:
        results["success"] = False
        results["message"] = f"❌ خطا در خواندن فایل: {str(e)}"
    
    return results