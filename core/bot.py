from bale import Bot, Message, CallbackQuery

from configs import TOKEN
from core.logging import is_seller

from keyboards.seller.account_book.main_menu_account_book import *
from keyboards.seller.main_menu_seller import *
from keyboards.seller.products_managment.prodocts_managment_keyboards import *

from texts.seller_texts import *

from callbacks.cb_main_menu_seller import *
from callbacks.cb_seller_account_book import *

from handlers.add_customer_to_db import add_customer

from datetime import datetime

import os  # اضافه کن
from datetime import datetime

user_state = {}
temp_customer = {}
temp_transaction = {}
temp_ecxel = {}
temp_product = {}

bot = Bot(TOKEN)

@bot.event
async def on_message(message: Message):
    """
    Chek the received message from the user and run it's code.

    Args:
        message(Message):
            Received message from the user.
    """
    print(f"Message from {message.chat.id}")
    if is_seller(message.chat.id) and message.chat.id in user_state:

        # ========== Get customer info
        if user_state[message.chat.id] == "waiting_for_name":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["name"] = message.text
            user_state[message.chat.id] = "waiting_for_phone"
            await message.reply(
                f"{CUSTOMER_NAME_RECEIVED_TEXT.format(name=message.text)}\n\n{ASK_CUSTOMER_PHONE_TEXT}",components=back_btn())
            return
        
        elif user_state[message.chat.id] == "waiting_for_phone":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["phone"] = message.text
            user_state[message.chat.id] = "waiting_for_amount"
            await message.reply(
                f"{CUSTOMER_PHONE_RECEIVED_TEXT.format(phone=message.text)}\n\n{ASK_CUSTOMER_DEBT_TEXT}",components=back_btn())
            return 
        
        elif user_state[message.chat.id] == "waiting_for_amount":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["amount"] = message.text
            user_state[message.chat.id] = "waiting_for_reason"
            await message.reply(
                f"{CUSTOMER_DEBT_RECEIVED_TEXT.format(amount=message.text)}\n\n{ASK_CUSTOMER_REASON_TEXT}",components=back_btn())
            return 
        
        elif user_state[message.chat.id] == "waiting_for_reason":
            if message.chat.id not in temp_customer:
                temp_customer[message.chat.id] = {}
            temp_customer[message.chat.id]["reason"] = message.text
            user_state[message.chat.id] = "waiting_for_confirmation"
            await message.reply(
                CUSTOMER_INFO_CONFIRM_TEXT.format(
                    name=temp_customer[message.chat.id]["name"],
                    phone=temp_customer[message.chat.id]["phone"],
                    amount=temp_customer[message.chat.id]["amount"],
                    reason=temp_customer[message.chat.id]["reason"]),components=apply_customer())       
            return
        elif user_state[message.chat.id] == "waiting_for_customer_phone":
            from handlers.get_customer_debt import get_customer_by_phone, get_total_debt
            
            customer = get_customer_by_phone(message.text)
            if not customer:
                await message.reply(CUSTOMER_NOT_FOUND_TEXT.format(phone=message.text), components=back_btn())
                user_state[message.chat.id] = None
                return
            
            total_debt = get_total_debt(customer["id"])
            temp_transaction[message.chat.id] = {
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "customer_phone": customer["phone"],
                "current_debt": total_debt}
            user_state[message.chat.id] = "waiting_for_debt_operation"
            await message.reply(
                CUSTOMER_DEBT_INFO_TEXT.format(
                    name=customer["name"],
                    phone=customer["phone"],
                    total_debt=total_debt),components=debt_operation_buttons())
        elif user_state[message.chat.id] == "waiting_for_increase_amount":
            try:
                amount = int(message.text)
                temp_transaction[message.chat.id]["amount"] = amount
                user_state[message.chat.id] = "waiting_for_increase_reason"
                await message.reply(
                    ASK_INCREASE_REASON_TEXT.format(name=temp_transaction[message.chat.id]["customer_name"]),
                    components=back_btn())
            except ValueError:
                await message.reply(INVALID_AMOUNT_ERROR_TEXT, components=back_btn())
        elif user_state[message.chat.id] == "waiting_for_increase_reason":
            temp_transaction[message.chat.id]["reason"] = message.text
            current = temp_transaction[message.chat.id]["current_debt"]
            amount = temp_transaction[message.chat.id]["amount"]
            new_debt = current + amount
            
            await message.reply(
                CONFIRM_DEBT_TRANSACTION_TEXT.format(
                    name=temp_transaction[message.chat.id]["customer_name"],
                    phone=temp_transaction[message.chat.id]["customer_phone"],
                    current_debt=current,
                    type="➕ افزایش بدهی",
                    amount=amount,
                    reason_label="علت افزایش",
                    reason=message.text,
                    new_debt=new_debt),components=confirm_debt_buttons())
            user_state[message.chat.id] = "waiting_for_confirm_debt"
        elif user_state[message.chat.id] == "waiting_for_decrease_amount":
            try:
                amount = int(message.text)
                if amount > temp_transaction[message.chat.id]["current_debt"]:
                    await message.reply(AMOUNT_EXCEEDS_DEBT_ERROR_TEXT, components=back_btn())
                    return
                temp_transaction[message.chat.id]["amount"] = amount
                user_state[message.chat.id] = "waiting_for_decrease_reason"
                await message.reply(
                    ASK_DECREASE_REASON_TEXT.format(name=temp_transaction[message.chat.id]["customer_name"]),
                    components=back_btn())
            except ValueError:
                await message.reply(INVALID_NUMBER_ERROR_TEXT, components=back_btn())
        elif user_state[message.chat.id] == "waiting_for_decrease_reason":
            temp_transaction[message.chat.id]["reason"] = message.text if message.text else "پرداخت بدهی"
            current = temp_transaction[message.chat.id]["current_debt"]
            amount = temp_transaction[message.chat.id]["amount"]
            new_debt = current - amount
            await message.reply(
                CONFIRM_DEBT_TRANSACTION_TEXT.format(
                    name=temp_transaction[message.chat.id]["customer_name"],
                    phone=temp_transaction[message.chat.id]["customer_phone"],
                    current_debt=current,
                    type="➖ کاهش بدهی",
                    amount=amount,
                    reason_label="توضیحات",
                    reason=temp_transaction[message.chat.id]["reason"],
                    new_debt=new_debt),components=confirm_debt_buttons())
            user_state[message.chat.id] = "waiting_for_confirm_debt"
        
        # ========== Receive excel ==========
        elif user_state[message.chat.id] == "waiting_for_ecxel":
            if message.document:
                file_name = message.document.file_name
                file_extension = file_name.split('.')[-1].lower()
                
                if file_extension in ['xlsx', 'csv']:
                    # دریافت فایل
                    file_content = await bot.get_file(message.document.file_id)
                    
                    # ذخیره فایل موقت
                    temp_file_path = f"temp_{file_name}"
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_content)
                    
                    # پردازش فایل
                    from handlers.add_ecxel_products_to_db import process_excel_file
                    result = process_excel_file(temp_file_path)
                    
                    # حذف فایل موقت
                    os.remove(temp_file_path)
                    
                    # ارسال نتیجه
                    await message.reply(result["message"], components=back_products_managment_menu())
                    user_state[message.chat.id] = None
                else:
                    await message.reply(EXCEL_INVALID_TEXT.format(file_extension=file_extension), components=back_products_managment_menu())
                    user_state[message.chat.id] = None
            else:
                await message.reply(EXCEL_NO_FILE_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None        
        # ========== Add product ==========
        elif user_state[message.chat.id] == "waiting_for_product_name":
            temp_product[message.chat.id]["product_name"] = message.text
            user_state[message.chat.id] = "waiting_for_product_brand"
            await message.reply(ASK_PRODUCT_BRAND_TEXT, components=back_products_managment_menu())

        elif user_state[message.chat.id] == "waiting_for_product_brand":
            temp_product[message.chat.id]["product_brand"] = message.text
            user_state[message.chat.id] = "waiting_for_price"
            await message.reply(ASK_PRODUCT_PRICE_TEXT, components=back_products_managment_menu())

        elif user_state[message.chat.id] == "waiting_for_price":
            temp_product[message.chat.id]["product_price"] = message.text
            user_state[message.chat.id] = "waiting_for_stock"
            await message.reply(ASK_PRODUCT_STOCK_TEXT, components=back_products_managment_menu())

        elif user_state[message.chat.id] == "waiting_for_stock":
            temp_product[message.chat.id]["product_stock"] = message.text
            user_state[message.chat.id] = "waiting_for_description"
            await message.reply(ASK_PRODUCT_DESCRIPTION_TEXT, components=back_products_managment_menu())

        elif user_state[message.chat.id] == "waiting_for_description":
            temp_product[message.chat.id]["product_description"] = message.text
            user_state[message.chat.id] = "waiting_for_image"
            await message.reply(ASK_PRODUCT_IMAGE_TEXT, components=back_products_managment_menu())

        elif user_state[message.chat.id] == "waiting_for_image":
            if message.photos:
                photo = message.photos[-1]
                try:
                    file_content = await bot.get_file(photo.file_id)
                    product_name = temp_product[message.chat.id].get("product_name", "unknown")
                    safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{safe_name}_{timestamp}.jpg"
                    IMAGES_FOLDER = "products_images"
                    if not os.path.exists(IMAGES_FOLDER):
                        os.makedirs(IMAGES_FOLDER)
                    filepath = os.path.join(IMAGES_FOLDER, filename)
                    with open(filepath, 'wb') as f:
                        f.write(file_content)
                    temp_product[message.chat.id]["product_image_path"] = filepath
                    temp_product[message.chat.id]["product_image"] = photo.file_id
                    print(f"image saved in : {filepath}")
                    user_state[message.chat.id] = "waiting_for_product_confirm"
                    await message.reply(
                        PRODUCT_CONFIRM_TEXT.format(
                            name=temp_product[message.chat.id]["product_name"],
                            brand=temp_product[message.chat.id]["product_brand"],
                            price=temp_product[message.chat.id]["product_price"],
                            stock=temp_product[message.chat.id]["product_stock"],
                            desc=temp_product[message.chat.id]["product_description"]),components=apply_products())
                except Exception as e:
                    print(f" خطا در ذخیره عکس: {e}")
                    await message.reply(IMAGE_SAVE_ERROR_TEXT, components=back_products_managment_menu())
            else:
                await message.reply(INVALID_IMAGE_TEXT, components=back_products_managment_menu())
    if message.text == '/start':
        if is_seller(message.chat.id):
            user_state[message.chat.id] = {}
            temp_customer[message.chat.id] = {}
            temp_transaction[message.chat.id] = {}
            temp_ecxel[message.chat.id] = {}
            temp_product[message.chat.id] = {}

            await message.reply(WELCOME_SELLER_TEXT, components=main_menu_seller())

@bot.event
async def on_callback(callback: CallbackQuery):
    """
    Check the callback and run it's code.

    Args:
        callback(CallbackQuery):
            Received callback from clicked button by user.
    """
    # ========== SELLER MAIN MENU ==========

    if callback.data == CB_BACK_TO_MAIN_MENU_SELLER:
        await callback.message.edit(WELCOME_SELLER_TEXT, components=main_menu_seller())
    # ========== ACCOUNT BOOK ==========

    elif callback.data == CB_SELLER_ACCOUNT_BOOK:
        await callback.message.edit(ACCOUNT_BOOK_TEXT, components=main_menu_account_book())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_ADD_CUSTOMER:
        user_state[callback.message.chat.id] = "waiting_for_name"
        temp_customer[callback.message.chat.id] = {}
        await callback.message.edit(ASK_CUSTOMER_NAME_TEXT, components=back_btn())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_APPLY_CUSTOMER:
        try:
            add_customer(name=temp_customer[callback.message.chat.id]["name"],
                        phone=temp_customer[callback.message.chat.id]["phone"],
                        amount=int(temp_customer[callback.message.chat.id]["amount"]),
                        reason=temp_customer[callback.message.chat.id]["reason"])
            print("customer info seccessfuly added to database!")
            await callback.message.edit(CUSTOMER_ADDED_SUCCESS_TEXT.format(
                name=temp_customer[callback.message.chat.id]["name"],
                phone=temp_customer[callback.message.chat.id]["phone"],
                amount=temp_customer[callback.message.chat.id]["amount"],
                reason=temp_customer[callback.message.chat.id]["reason"],
                date=datetime.now().strftime("%Y/%m/%d")), components=back_btn())
        except:
            await callback.message.edit(CUSTOMER_ADD_FAILED_TEXT, components=back_btn())
            
    elif callback.data == CB_SELLER_ACCOUNT_BOOK_EDIT_CUSTOMER:
        user_state[callback.message.chat.id] = "waiting_for_customer_phone"
        temp_transaction[callback.message.chat.id] = {}
        await callback.message.edit(ASK_CUSTOMER_PHONE_FOR_DEBT, components=back_btn())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_INCREASE_DEBT:
        temp_transaction[callback.message.chat.id]["type"] = "increase"
        user_state[callback.message.chat.id] = "waiting_for_increase_amount"
        await callback.message.edit(
            ASK_INCREASE_AMOUNT_TEXT.format(name=temp_transaction[callback.message.chat.id]["customer_name"]),components=back_btn())

    elif callback.data == CB_SELLER_ACCOUNT_BOOK_DECREASE_DEBT:
        temp_transaction[callback.message.chat.id]["type"] = "decrease"
        user_state[callback.message.chat.id] = "waiting_for_decrease_amount"
        await callback.message.edit(
            ASK_DECREASE_AMOUNT_TEXT.format(name=temp_transaction[callback.message.chat.id]["customer_name"]),components=back_btn())
        
    elif callback.data == CB_SELLER_ACCOUNT_BOOK_CONFIRM_DEBT:
        from handlers.get_customer_debt import add_transaction
        trans = temp_transaction[callback.message.chat.id]
        if trans["type"] == "increase":
            amount = trans["amount"]
            type_text = "افزایش بدهی"
        else:
            amount = -trans["amount"]
            type_text = "کاهش بدهی"
        add_transaction(trans["customer_id"], amount, trans["reason"])
        await callback.message.edit(
            DEBT_TRANSACTION_SUCCESS_TEXT.format(
                name=trans["customer_name"],
                type=type_text,
                amount=trans["amount"],
                new_debt=trans["current_debt"] + amount,
                date=datetime.now().strftime("%Y/%m/%d")),components=back_btn())
        user_state[callback.message.chat.id] = None
        temp_transaction.pop(callback.message.chat.id, None)


    elif callback.data == CB_SELLER_ACCOUNT_BOOK_GET_PDF:
        from handlers.customer_debt_report import send_customers_debt_pdf
        await send_customers_debt_pdf(callback) 

    # ========== PRODUCTS MANAGMENT ==========
    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT:
        await callback.message.edit(PRODUCTS_MANAGEMENT_TEXT, components=main_menu_products_managment())

    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_ADD_ECXEL:
        user_state[callback.message.chat.id] = "waiting_for_ecxel"
        await callback.message.edit(EXCEL_UPLOAD_GUIDE_TEXT, components=back_products_managment_menu())
        
    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_ADD_PRODUCT:
        user_state[callback.message.chat.id] = "waiting_for_product_name"
        temp_product[callback.message.chat.id] = {}
        await callback.message.edit(ASK_PRODUCT_NAME_TEXT, components=back_products_managment_menu())

    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_PRODUCTS_LIST:
        from handlers.products_report import send_products_report_pdf
        await send_products_report_pdf(callback)
        
    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_PRICE_CHANGE:
        pass

    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_APPLY_DISCOUNT:
        pass

    elif callback.data == CB_SELLER_APPLY_PRODUCTS:
        from handlers.add_product_to_db import add_product_from_dict
        product_data = temp_product[callback.message.chat.id]
        try:
            price_str = str(product_data.get("product_price", "0"))
            stock_str = str(product_data.get("product_stock", "0"))
            price_str = price_str.replace(',', '').replace(' ', '')
            stock_str = stock_str.replace(',', '').replace(' ', '')
            price = int(price_str)
            stock = int(stock_str)
        except ValueError:
            await callback.message.edit(
                "❌ خطا: قیمت و موجودی باید عدد باشند.\n\nلطفاً مجدداً تلاش کنید.",
                components=back_products_managment_menu())
            return
        
        product_dict = {
            "name": product_data.get("product_name", ""),
            "brand": product_data.get("product_brand", ""),
            "price": price,
            "stock": stock,
            "description": product_data.get("product_description", ""),
            "image_path": product_data.get("product_image_path", "")}
        result = add_product_from_dict(product_dict)
        if result["success"]:
            if result["is_new"]:
                message_text = PRODUCT_ADDED_SUCCESS_TEXT.format(
                    product_id=result["product_id"],
                    name=result["name"],
                    brand=result["brand"],
                    price=result["price"],
                    stock=result["stock"])
            else:
                message_text = PRODUCT_UPDATED_SUCCESS_TEXT.format(
                    product_id=result["product_id"],
                    name=product_data.get("product_name", ""),
                    brand=product_data.get("product_brand", ""),
                    old_price=result["old_price"],
                    new_price=result["new_price"],
                    old_stock=result["old_stock"],
                    added_stock=result["added_stock"],
                    new_stock=result["new_stock"])
            await callback.message.edit(message_text, components=back_products_managment_menu())
            user_state[callback.message.chat.id] = None
            temp_product.pop(callback.message.chat.id, None)
        else:
            await callback.message.edit(
                f"❌ خطا در ثبت محصول:\n\n{result['message']}",
                components=back_products_managment_menu())
if __name__ == "__main__":
    bot.run()