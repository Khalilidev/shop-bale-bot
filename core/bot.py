from bale import Bot, Message, CallbackQuery

from configs import TOKEN
from core.logging import is_seller

from keyboards.seller.account_book.main_menu_account_book import *
from keyboards.seller.main_menu_seller import *
from keyboards.seller.products_managment.prodocts_managment_keyboards import *

from texts.seller_texts import *
from texts.customer_texts import *

from callbacks.cb_main_menu_seller import *
from callbacks.cb_seller_account_book import *
from callbacks.cb_seller_send_message import *

from handlers.add_customer_to_db import add_customer

from datetime import datetime

import os
from datetime import datetime

from handlers.product_editor import get_product_by_id, get_delete_confirmation_keyboard, delete_product
from handlers.clear_state import clear_user_state
from handlers.categories import get_category_keyboard, CATEGORIES
from keyboards.seller.products_managment.prodocts_managment_keyboards import edit_product_back_keyboard

user_state = {}
temp_customer = {}
temp_transaction = {}
temp_ecxel = {}
temp_product = {}
temp_id = {}
temp_message = {}
temp_contact = {}

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
            user_state[message.chat.id] = "waiting_for_product_category"
            await message.reply(ASK_PRODUCT_CATEGORY_TEXT, components=get_category_keyboard(CB_SELLER_PRODUCT_CATEGORY_SELECTED))

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
                    category = temp_product[message.chat.id].get("product_category", "بدون دسته‌بندی")
                    await message.reply(
                        PRODUCT_CONFIRM_TEXT.format(
                            name=temp_product[message.chat.id]["product_name"],
                            brand=temp_product[message.chat.id]["product_brand"],
                            category=category,
                            price=temp_product[message.chat.id]["product_price"],
                            stock=temp_product[message.chat.id]["product_stock"],
                            desc=temp_product[message.chat.id]["product_description"]),components=apply_products())
                except Exception as e:
                    print(f" خطا در ذخیره عکس: {e}")
                    await message.reply(IMAGE_SAVE_ERROR_TEXT, components=back_products_managment_menu())
            else:
                await message.reply(INVALID_IMAGE_TEXT, components=back_products_managment_menu())
        # ========== Edit product ==========
        elif user_state[message.chat.id] == "waiting_for_product_id":
            try:
                product_id = int(message.text.strip())
                from handlers.product_editor import get_product_by_id, format_product_info, get_product_edit_keyboard
                
                product = get_product_by_id(product_id)
                
                if product:
                    has_image = bool(product.get("path_image") and os.path.exists(product.get("path_image", "")))
                    info_text = format_product_info(product)
                    
                    await message.reply(
                        info_text,
                        components=get_product_edit_keyboard(product_id, has_image)
                    )
                    user_state[message.chat.id] = None
                else:
                    await message.reply(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())
                    user_state[message.chat.id] = None
            except ValueError:
                await message.reply("❌ لطفاً یک عدد معتبر به عنوان شناسه محصول وارد کنید.\nمثال: 123", components=back_products_managment_menu())
        #! ========== send message module ==========
        elif user_state[message.chat.id] == "waiting_for_broadcast":
            if message.chat.id not in temp_message:
                temp_message[message.chat.id] = {}
            temp_message[message.chat.id]["message"] = message.text
            from keyboards.seller.send_message.send_message_keyborads import broadcast_confirm_keyboard
            await message.reply(BROADCAST_CONFIRM_TEXT.format(message=message.text), components=broadcast_confirm_keyboard())

        #! ========== Edit contact module ==========
        elif user_state[message.chat.id] == "waiting_for_edit_contact":
            if message.chat.id not in temp_contact:
                temp_contact[message.chat.id] = {}
            temp_contact[message.chat.id]["contact"] = message.text
            from handlers.contact import edit_contact
            from keyboards.seller.send_message.send_message_keyborads import back_to_main_menu_seller
            try:
                edit_contact(text=temp_contact[message.chat.id]["contact"])
                await message.reply(CONTACT_UPDATED_SUCCESS_TEXT, components=back_to_main_menu_seller())
            except:
                await message.reply(CONTACT_UPDATE_ERROR_TEXT, components=back_to_main_menu_seller())
        # ========== Edit product - receive new values ==========
        state = user_state[message.chat.id]
        if state and isinstance(state, str):
            if state.startswith("edit_product_name:"):
                product_id = int(state.split(":")[-1])
                new_name = message.text.strip()
                
                if new_name:
                    from handlers.product_editor import update_product_field
                    if update_product_field(product_id, "name", new_name):
                        await message.reply(FIELD_UPDATED_SUCCESS_TEXT.format(field="نام", new_value=new_name), components=back_products_managment_menu())
                    else:
                        await message.reply(PRODUCT_UPDATE_NAME_ERROR_TEXT, components=back_products_managment_menu())
                else:
                    await message.reply(PRODUCT_EMPTY_NAME_ERROR_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None

            elif state.startswith("edit_product_brand:"):
                product_id = int(state.split(":")[-1])
                new_brand = message.text.strip()
                
                if new_brand:
                    from handlers.product_editor import update_product_field
                    if update_product_field(product_id, "brand", new_brand):
                        await message.reply(FIELD_UPDATED_SUCCESS_TEXT.format(field="برند", new_value=new_brand), components=back_products_managment_menu())
                    else:
                        await message.reply(PRODUCT_UPDATE_BRAND_ERROR_TEXT, components=back_products_managment_menu())
                else:
                    await message.reply(PRODUCT_EMPTY_BRAND_ERROR_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None

            elif state.startswith("edit_product_price:"):
                product_id = int(state.split(":")[-1])
                try:
                    new_price = int(message.text.replace(',', '').replace(' ', ''))
                    if new_price > 0:
                        from handlers.product_editor import update_product_field
                        if update_product_field(product_id, "price", new_price):
                            await message.reply(FIELD_UPDATED_SUCCESS_TEXT.format(field="قیمت", new_value=f"{new_price:,} تومان"), components=back_products_managment_menu())
                        else:
                            await message.reply(PRODUCT_UPDATE_PRICE_ERROR_TEXT, components=back_products_managment_menu())
                    else:
                        await message.reply(PRODUCT_PRICE_ZERO_ERROR_TEXT, components=back_products_managment_menu())
                except ValueError:
                    await message.reply(INVALID_NUMBER_ERROR_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None

            elif state.startswith("edit_product_stock:"):
                product_id = int(state.split(":")[-1])
                try:
                    new_stock = int(message.text.replace(',', '').replace(' ', ''))
                    if new_stock >= 0:
                        from handlers.product_editor import update_product_field
                        if update_product_field(product_id, "stock_quantity", new_stock):
                            await message.reply(FIELD_UPDATED_SUCCESS_TEXT.format(field="موجودی", new_value=f"{new_stock} عدد"), components=back_products_managment_menu())
                        else:
                            await message.reply(PRODUCT_UPDATE_STOCK_ERROR_TEXT, components=back_products_managment_menu())
                    else:
                        await message.reply(PRODUCT_STOCK_NEGATIVE_ERROR_TEXT, components=back_products_managment_menu())
                except ValueError:
                    await message.reply(INVALID_NUMBER_ERROR_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None

            elif state.startswith("edit_product_description:"):
                product_id = int(state.split(":")[-1])
                new_description = message.text.strip()
                
                from handlers.product_editor import update_product_field
                if update_product_field(product_id, "description", new_description):
                    await message.reply(FIELD_UPDATED_SUCCESS_TEXT.format(field="توضیحات", new_value=new_description if new_description else "(خالی)"), components=back_products_managment_menu())
                else:
                    await message.reply(PRODUCT_UPDATE_DESCRIPTION_ERROR_TEXT, components=back_products_managment_menu())
                user_state[message.chat.id] = None

            elif state.startswith("edit_product_image:"):
                product_id = int(state.split(":")[-1])
                
                if message.photos:
                    photo = message.photos[-1]
                    try:
                        file_content = await bot.get_file(photo.file_id)
                        product_name = temp_product[message.chat.id].get("product_name", "product")
                        
                        from handlers.product_editor import save_product_image
                        filepath = save_product_image(product_id, file_content, product_name)
                        
                        if filepath:
                            await message.reply(
                                PRODUCT_IMAGE_UPDATED_SUCCESS_TEXT.format(filepath=filepath),
                                components=back_products_managment_menu()
                            )
                        else:
                            await message.reply(IMAGE_SAVE_ERROR_TEXT, components=back_products_managment_menu())
                    except Exception as e:
                        print(f"Error saving image: {e}")
                        await message.reply(IMAGE_SAVE_ERROR_TEXT, components=back_products_managment_menu())
                else:
                    await message.reply(INVALID_IMAGE_TEXT, components=edit_product_back_keyboard())
                    return
                
                user_state[message.chat.id] = None
                temp_product.pop(message.chat.id, None)                
                user_state[message.chat.id] = None
                temp_product.pop(message.chat.id, None)
            # ========== Edit product - category ==========
            elif state.startswith("edit_product_category:"):
                product_id = int(state.split(":")[-1])
                pass
    else:
        ################################################################ !
        # !               handling the customer                          #
        #################################################################!
        pass
    if message.text == '/start':
        from handlers.add_users import new_user
        new_user(message.chat.id, message.chat.username)
        clear_user_state(user_state, temp_customer, temp_transaction, temp_ecxel,temp_product, temp_id, temp_message, temp_contact,message.chat.id)
        if is_seller(message.chat.id):
            await message.reply(WELCOME_SELLER_TEXT, components=main_menu_seller())
        else :
            from keyboards.customer.main_menu_customer import main_menu_customer
            await message.reply(CUSTOMER_WELLCOME_MESSAGE, components=main_menu_customer())

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
        clear_user_state(user_state, temp_customer, temp_transaction, temp_ecxel,temp_product, temp_id, temp_message, temp_contact,callback.message.chat.id)
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
        
    elif callback.data == CB_SELLER_PRODUCTS_MANAGMENT_PRODUCT_EDIT:
        user_state[callback.message.chat.id] = "waiting_for_product_id"
        await callback.message.edit(ASK_PRODUCT_ID_TEXT, components=back_products_managment_menu())

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
            "category": product_data.get("product_category", "بدون دسته‌بندی"),
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
    # ========== PRODUCT EDITING CALLBACKS ==========
    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_NAME + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_name:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            await callback.message.edit(
                ASK_NEW_NAME_TEXT.format(current=product['name']),
                components=edit_product_back_keyboard())
            
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_BRAND + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_brand:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            await callback.message.edit(
                ASK_NEW_BRAND_TEXT.format(current=product['brand']),
                components=edit_product_back_keyboard())
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_PRICE + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_price:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            await callback.message.edit(
                ASK_NEW_PRICE_TEXT.format(current=product['price']),
                components=edit_product_back_keyboard())
            
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_STOCK + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_stock:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            await callback.message.edit(
                ASK_NEW_STOCK_TEXT.format(current=product['stock']),
                components=edit_product_back_keyboard())
            
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_DESCRIPTION + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_description:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            current_desc = product['description'] if product['description'] else "(بدون توضیحات)"
            await callback.message.edit(
                ASK_NEW_DESCRIPTION_TEXT.format(current=current_desc),
                components=edit_product_back_keyboard())
            
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_IMAGE + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_image:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id, "product_name": product['name']}
            await callback.message.edit(
                ASK_NEW_IMAGE_TEXT,
                components=edit_product_back_keyboard())
            
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_DELETE + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            await callback.message.edit(
                PRODUCT_DELETE_CONFIRM_TEXT.format(product_name=product['name']),
                components=get_delete_confirmation_keyboard(product_id, product['name']))
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data.startswith(CB_SELLER_PRODUCT_DELETE_CONFIRM + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            if delete_product(product_id):
                await callback.message.edit(
                    PRODUCT_DELETED_SUCCESS_TEXT.format(product_id=product_id, product_name=product['name']),
                    components=back_products_managment_menu())
            else:
                await callback.message.edit(PRODUCT_DELETED_FAILED_TEXT, components=back_products_managment_menu())
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())

    elif callback.data == CB_SELLER_PRODUCT_BACK_TO_MENU:
        user_state[callback.message.chat.id] = None
        temp_product.pop(callback.message.chat.id, None)
        clear_user_state(user_state, temp_customer, temp_transaction, temp_ecxel,temp_product, temp_id, temp_message, temp_contact,callback.message.chat.id)
        await callback.message.edit(PRODUCTS_MANAGEMENT_TEXT, components=main_menu_products_managment())

    #! ========== send message module ==========
    elif callback.data == CB_SELLER_SEND_MESSAGE:
        from keyboards.seller.send_message.send_message_keyborads import back_to_main_menu_seller
        user_state[callback.message.chat.id] = "waiting_for_broadcast"
        await callback.message.edit(SEND_MESSAGE_TEXT, components=back_to_main_menu_seller())

    elif callback.data == CB_BROADCAST_CONFIRM:
        from handlers.send_message import send_message_to_customers
        from keyboards.seller.send_message.send_message_keyborads import back_to_main_menu_seller
        if callback.message.chat.id not in temp_message:
            await callback.message.edit(NO_MESSAGE_TO_SEND_TEXT, components=back_to_main_menu_seller())
            return
        if "message" not in temp_message[callback.message.chat.id]:
            await callback.message.edit(NO_MESSAGE_TO_SEND_TEXT, components=back_to_main_menu_seller())
            return
        message_text = temp_message[callback.message.chat.id]["message"]
        await send_message_to_customers(bot, text=message_text)
        await callback.message.edit(BROADCAST_SUCCESS_TEXT, components=back_to_main_menu_seller())
        temp_message.pop(callback.message.chat.id, None)


    # ========== Edit category ==========
    elif callback.data.startswith(CB_SELLER_PRODUCT_EDIT_CATEGORY + ":"):
        product_id = int(callback.data.split(":")[-1])
        product = get_product_by_id(product_id)
        
        if product:
            user_state[callback.message.chat.id] = f"edit_product_category:{product_id}"
            temp_product[callback.message.chat.id] = {"product_id": product_id}
            await callback.message.edit(
                ASK_NEW_CATEGORY_TEXT.format(current=product.get('category', 'بدون دسته‌بندی')),
                components=get_category_keyboard(CB_SELLER_PRODUCT_CATEGORY_SELECTED))
        else:
            await callback.message.edit(PRODUCT_NOT_FOUND_TEXT.format(product_id=product_id), components=back_products_managment_menu())
    # ========== Category selection callback ==========
    elif callback.data.startswith(CB_SELLER_PRODUCT_CATEGORY_SELECTED + ":"):
        category = callback.data.split(":", 1)[-1]
        
        if category not in CATEGORIES:
            await callback.message.edit(
                CATEGORY_NOT_FOUND_TEXT,
                components=back_products_managment_menu())
            return
        
        current_state = user_state.get(callback.message.chat.id, "")
        
        # حالت ویرایش دسته‌بندی
        if current_state and current_state.startswith("edit_product_category:"):
            product_id = int(current_state.split(":")[-1])
            from handlers.product_editor import update_product_field
            
            if update_product_field(product_id, "category", category):
                await callback.message.edit(
                    CATEGORY_UPDATED_SUCCESS_TEXT.format(new_value=category),
                    components=back_products_managment_menu())
            else:
                await callback.message.edit(
                    CATEGORY_UPDATE_ERROR_TEXT,
                    components=back_products_managment_menu())
            
            user_state[callback.message.chat.id] = None
            temp_product.pop(callback.message.chat.id, None)
        
        # حالت افزودن محصول جدید
        elif current_state == "waiting_for_product_category":
            temp_product[callback.message.chat.id]["product_category"] = category
            user_state[callback.message.chat.id] = "waiting_for_product_brand"
            await callback.message.edit(
                CATEGORY_SELECTED_TEXT.format(category=category) + "\n\n" + ASK_PRODUCT_BRAND_TEXT,
                components=back_products_managment_menu())
        
        else:
            # اگر حالت نامشخص بود، خطا بده
            await callback.message.edit(
                "❌ خطا: وضعیت نامعتبر. لطفاً دوباره تلاش کنید.",
                components=back_products_managment_menu())

    #! ========== Edit contact ==========
    elif callback.data == CB_EDIT_CONTACT:
        user_state[callback.message.chat.id] = "waiting_for_edit_contact"
        from keyboards.seller.send_message.send_message_keyborads import back_to_main_menu_seller
        from handlers.get_contact_text import get_text
        await callback.message.edit(EDIT_CONTACT_HELP_TEXT.format(current_value=get_text()),components=back_to_main_menu_seller())




    ################################################################ !
    # !               handling the customer                          #
    #################################################################!
if __name__ == "__main__":
    bot.run()