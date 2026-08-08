from bale import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.cb_seller_reports import *
from handlers.order_details_report import send_order_details_pdf
from callbacks.cb_main_menu_seller import CB_BACK_TO_MAIN_MENU_SELLER
import sqlite3
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════
# Database helpers
# ══════════════════════════════════════════════════════════════════════════

def get_db_connection():
    """
    Create and return a connection to the SQLite database.
    """
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_orders_by_status(status: str, limit: int = 100):
    """
    Get orders based on their status.

    Args:
        status: Order status ('pending', 'confirmed', 'cancelled').
        limit: Maximum number of orders to fetch.

    Returns:
        list[dict]: List of orders.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            id,
            customer_name,
            customer_phone,
            customer_address,
            customer_note,
            total_price,
            status,
            created_at,
            confirmed_at,
            cancelled_at
        FROM orders
        WHERE status = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (status, limit))

    orders = []
    for row in cur.fetchall():
        orders.append(dict(row))

    conn.close()
    return orders


def update_order_status(order_id: int, new_status: str) -> bool:
    """
    Update the status of an order.

    Args:
        order_id: The order ID.
        new_status: New status ('confirmed' or 'cancelled').

    Returns:
        bool: True if the update was successful, otherwise False.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Set the appropriate timestamp based on the new status.
        if new_status == 'confirmed':
            cur.execute("""
                UPDATE orders 
                SET status = ?, confirmed_at = ?
                WHERE id = ?
            """, (new_status, datetime.now(), order_id))

        elif new_status == 'cancelled':
            cur.execute("""
                UPDATE orders 
                SET status = ?, cancelled_at = ?
                WHERE id = ?
            """, (new_status, datetime.now(), order_id))

        else:
            cur.execute("""
                UPDATE orders 
                SET status = ?
                WHERE id = ?
            """, (new_status, order_id))

        conn.commit()
        success = cur.rowcount > 0
        conn.close()
        return success

    except Exception as e:
        print(f"Error updating order status: {e}")
        conn.close()
        return False


def decrease_product_stock(order_id: int) -> bool:
    """
    Decrease product stock based on the items in an order.

    Args:
        order_id: The order ID.

    Returns:
        bool: True if stock was decreased successfully, otherwise False.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get all items inside the order.
        cur.execute("""
            SELECT product_id, quantity
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))

        items = cur.fetchall()

        for item in items:
            product_id, quantity = item

            # Check current stock of the product.
            cur.execute("""
                SELECT stock_quantity 
                FROM products 
                WHERE id = ?
            """, (product_id,))

            result = cur.fetchone()

            if not result:
                conn.close()
                return False

            current_stock = result[0]

            # If stock is not enough, cancel the whole operation.
            if current_stock < quantity:
                conn.close()
                return False

            # Decrease stock.
            cur.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - ?
                WHERE id = ?
            """, (quantity, product_id))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error decreasing stock: {e}")
        conn.close()
        return False


def save_to_confirmed_tables(order_id: int) -> bool:
    """
    Copy a confirmed order and its items into separate archive tables.

    Args:
        order_id: The order ID.

    Returns:
        bool: True if the data was archived successfully, otherwise False.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Get the main order data.
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cur.fetchone()

        if not order:
            return False

        # 2. Insert order data into confirmed_orders table.
        cur.execute("""
            INSERT INTO confirmed_orders (
                original_order_id, customer_name, customer_phone, 
                customer_address, customer_note, total_price
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order['id'],
            order['customer_name'],
            order['customer_phone'],
            order['customer_address'],
            order['customer_note'],
            order['total_price']
        ))

        # Get the new archive order ID.
        new_confirmed_order_id = cur.lastrowid

        # 3. Get all items of this order.
        cur.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        items = cur.fetchall()

        # 4. Insert order items into confirmed_order_items table.
        for item in items:
            cur.execute("""
                INSERT INTO confirmed_order_items (
                    confirmed_order_id, product_id, quantity, price
                ) VALUES (?, ?, ?, ?)
            """, (
                new_confirmed_order_id,
                item['product_id'],
                item['quantity'],
                item['price']
            ))

        conn.commit()
        return True

    except Exception as e:
        print(f"Error copying to confirmed tables: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_order_by_id(order_id: int):
    """
    Get a single order by its ID.

    Args:
        order_id: The order ID.

    Returns:
        dict | None: Order data if found, otherwise None.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            id,
            customer_name,
            customer_phone,
            customer_address,
            customer_note,
            total_price,
            status,
            created_at,
            confirmed_at,
            cancelled_at
        FROM orders
        WHERE id = ?
    """, (order_id,))

    row = cur.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None


def get_order_items(order_id: int):
    """
    Get all items of a specific order.

    Args:
        order_id: The order ID.

    Returns:
        list[dict]: List of order items.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            oi.id,
            oi.product_id,
            oi.quantity,
            oi.price,
            p.name as product_name,
            p.brand as product_brand
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,))

    items = []
    for row in cur.fetchall():
        items.append(dict(row))

    conn.close()
    return items


# ══════════════════════════════════════════════════════════════════════════
# Message formatting helpers
# ══════════════════════════════════════════════════════════════════════════

def format_order_text(order: dict, index: int, total: int) -> str:
    """
    Format order data into a readable message.

    Args:
        order: Order dictionary.
        index: Current order index in the list.
        total: Total number of orders in the list.

    Returns:
        str: Formatted order message.
    """
    status_emoji = {
        'pending': '🆕',
        'confirmed': '✅',
        'cancelled': '❌'
    }

    status_text = {
        'pending': 'در انتظار تأیید',
        'confirmed': 'تأیید شده',
        'cancelled': 'لغو شده'
    }

    text = f"📋 **سفارش {index + 1} از {total}**\n\n"

    text += f"🆔 شناسه: {order['id']}\n"
    text += f"👤 مشتری: {order['customer_name']}\n"
    text += f"📱 تلفن: {order['customer_phone']}\n"

    if order.get('customer_address'):
        text += f"📍 آدرس: {order['customer_address']}\n"

    if order.get('customer_note'):
        text += f"📝 یادداشت: {order['customer_note']}\n"

    text += f"💰 مبلغ کل: {order['total_price']:,} تومان\n"
    text += f"📊 وضعیت: {status_emoji.get(order['status'], '')} {status_text.get(order['status'], order['status'])}\n"
    text += f"📅 تاریخ ثبت: {order['created_at']}\n"

    if order.get('confirmed_at'):
        text += f"✅ تاریخ تأیید: {order['confirmed_at']}\n"

    if order.get('cancelled_at'):
        text += f"❌ تاریخ لغو: {order['cancelled_at']}\n"

    return text


# ══════════════════════════════════════════════════════════════════════════
# Keyboard builders
# ══════════════════════════════════════════════════════════════════════════

def get_order_navigation_keyboard(order_id: int, index: int, total: int, status: str):
    """
    Build the navigation keyboard for an order.

    Args:
        order_id: Current order ID.
        index: Current order index.
        total: Total number of orders.
        status: Order list status ('pending', 'confirmed', 'cancelled').

    Returns:
        InlineKeyboardMarkup: Order keyboard.
    """
    keyboard = InlineKeyboardMarkup()

    # Order details button.
    btn_details = InlineKeyboardButton(
        "📄 دیدن جزئیات سفارش",
        callback_data=f"{CB_SELLER_REPORTS_SHOW_DETAILS}:{order_id}"
    )

    # Previous / next navigation buttons.
    btn_prev = InlineKeyboardButton(
        "◀️ قبلی",
        callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_PREV}:{index}:{status}"
    )

    btn_next = InlineKeyboardButton(
        "بعدی ▶️",
        callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_NEXT}:{index}:{status}"
    )

    # Action buttons are only available for pending orders.
    if status == 'pending':
        btn_confirm = InlineKeyboardButton(
            "✅ ثبت سفارش",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CONFIRM_ORDER}:{order_id}"
        )

        btn_cancel = InlineKeyboardButton(
            "❌ لغو کردن سفارش",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER}:{order_id}"
        )

        keyboard.add(btn_details, row=1)
        keyboard.add(btn_confirm, row=2)
        keyboard.add(btn_cancel, row=3)

    else:
        keyboard.add(btn_details, row=1)

    # Add navigation buttons only when there is more than one order.
    if total > 1:
        if index == 0:
            keyboard.add(btn_next, row=4)

        elif index == total - 1:
            keyboard.add(btn_prev, row=4)

        else:
            keyboard.add(btn_next, row=4)
            keyboard.add(btn_prev, row=4)

    # Back button.
    btn_back = InlineKeyboardButton(
        "🔙 بازگشت",
        callback_data=CB_BACK_TO_MAIN_MENU_SELLER
    )

    keyboard.add(btn_back, row=5)

    return keyboard


def get_confirm_cancel_keyboard(order_id: int, action: str):
    """
    Build the final confirmation keyboard for confirming or cancelling an order.

    Args:
        order_id: The order ID.
        action: Action type ('confirm' or 'cancel').

    Returns:
        tuple: (keyboard, confirmation text)
    """
    keyboard = InlineKeyboardMarkup()

    if action == 'confirm':
        btn_yes = InlineKeyboardButton(
            "✅ بله، تأیید می‌کنم",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CONFIRM_ORDER}_FINAL:{order_id}"
        )

        btn_no = InlineKeyboardButton(
            "❌ نه، انصراف",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER}_BACK:{order_id}"
        )

        text = (
            "⚠️ **تأیید نهایی سفارش**\n\n"
            "آیا از تأیید این سفارش اطمینان دارید؟\n"
            "پس از تأیید، موجودی محصولات کاهش می‌یابد."
        )

    else:
        btn_yes = InlineKeyboardButton(
            "❌ بله، لغو می‌کنم",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER}_FINAL:{order_id}"
        )

        btn_no = InlineKeyboardButton(
            "✅ نه، انصراف",
            callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER}_BACK:{order_id}"
        )

        text = (
            "⚠️ **لغو نهایی سفارش**\n\n"
            "آیا از لغو این سفارش اطمینان دارید؟\n"
            "این عمل غیرقابل بازگشت است!"
        )

    keyboard.add(btn_yes, row=1)
    keyboard.add(btn_no, row=2)

    btn_back = InlineKeyboardButton(
        "🔙 بازگشت",
        callback_data=f"{CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER}_BACK:{order_id}"
    )

    keyboard.add(btn_back, row=3)

    return keyboard, text


# ══════════════════════════════════════════════════════════════════════════
# Callback manager
# ══════════════════════════════════════════════════════════════════════════

async def order_manager(callback: CallbackQuery):
    """
    Handle all callbacks related to order reports.
    """
    chat_id = callback.message.chat.id

    # ──────────────────────────────────────────────────────────────────────
    # 1. Show the first pending order
    # ──────────────────────────────────────────────────────────────────────
    if callback.data == CB_SELLER_REPORTS_NEW_ORDERS:
        orders = get_orders_by_status('pending')

        if not orders:
            await callback.message.edit(
                "🆕 **سفارش‌های جدید**\n\nهیچ سفارش جدیدی وجود ندارد.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = orders[0]
        text = format_order_text(order, 0, len(orders))
        keyboard = get_order_navigation_keyboard(order['id'], 0, len(orders), 'pending')

        await callback.message.edit(text, components=keyboard)
        return

    # ──────────────────────────────────────────────────────────────────────
    # 2. Navigate between pending orders
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_NEXT) or callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_PREV):
        orders = get_orders_by_status('pending')

        if not orders:
            await callback.message.edit(
                "🆕 **سفارش‌های جدید**\n\nهیچ سفارش جدیدی وجود ندارد.",
                components=get_back_to_reports_keyboard()
            )
            return

        parts = callback.data.split(":")

        try:
            current_index = int(parts[-2])
            status_from_callback = parts[-1]

            if status_from_callback == 'pending':
                if callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_NEXT):
                    new_index = min(current_index + 1, len(orders) - 1)
                else:
                    new_index = max(current_index - 1, 0)

                order = orders[new_index]
                text = format_order_text(order, new_index, len(orders))
                keyboard = get_order_navigation_keyboard(order['id'], new_index, len(orders), 'pending')

                await callback.message.edit(text, components=keyboard)
                return

        except (ValueError, IndexError) as e:
            print(f"Error in navigation: {e}")

            # If navigation fails, show the first order.
            order = orders[0]
            text = format_order_text(order, 0, len(orders))
            keyboard = get_order_navigation_keyboard(order['id'], 0, len(orders), 'pending')

            await callback.message.edit(text, components=keyboard)
            return

    # ──────────────────────────────────────────────────────────────────────
    # 3. Show confirmed orders list
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data == CB_SELLER_REPORTS_CONFIRMED_ORDERS:
        orders = get_orders_by_status('confirmed')

        if not orders:
            await callback.message.edit(
                "✅ **سفارش‌های تأیید شده**\n\nهیچ سفارش تأیید شده‌ای وجود ندارد.",
                components=get_back_to_reports_keyboard()
            )
            return

        text = "✅ **سفارش‌های تأیید شده**\n\n"

        for i, order in enumerate(orders, 1):
            text += f"{i}. سفارش #{order['id']} - {order['customer_name']} - {order['total_price']:,} تومان\n"

        text += f"\nتعداد کل: {len(orders)} سفارش"

        await callback.message.edit(text, components=get_back_to_reports_keyboard())

    # ──────────────────────────────────────────────────────────────────────
    # 4. Show cancelled orders list
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data == CB_SELLER_REPORTS_CANCELLED_ORDERS:
        orders = get_orders_by_status('cancelled')

        if not orders:
            await callback.message.edit(
                "❌ **سفارش‌های لغو شده**\n\nهیچ سفارش لغو شده‌ای وجود ندارد.",
                components=get_back_to_reports_keyboard()
            )
            return

        text = "❌ **سفارش‌های لغو شده**\n\n"

        for i, order in enumerate(orders, 1):
            text += f"{i}. سفارش #{order['id']} - {order['customer_name']} - {order['total_price']:,} تومان\n"

        text += f"\nتعداد کل: {len(orders)} سفارش"

        await callback.message.edit(text, components=get_back_to_reports_keyboard())

    # ──────────────────────────────────────────────────────────────────────
    # 5. Confirm order - first step
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_CONFIRM_ORDER) and "_FINAL" not in callback.data:
        try:
            order_id = int(callback.data.split(":")[-1])

        except (ValueError, IndexError):
            await callback.message.edit(
                "❌ خطا در دریافت اطلاعات سفارش.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = get_order_by_id(order_id)

        if not order:
            await callback.message.edit(
                "❌ سفارش مورد نظر یافت نشد.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Make sure the order is still pending.
        if order['status'] != 'pending':
            await callback.message.edit(
                f"❌ این سفارش قبلاً { 'تأیید' if order['status'] == 'confirmed' else 'لغو' } شده است.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Show final confirmation keyboard.
        keyboard, text = get_confirm_cancel_keyboard(order_id, 'confirm')
        order_text = format_order_text(order, 0, 1)

        await callback.message.edit(
            order_text + "\n\n" + text,
            components=keyboard
        )

    # ──────────────────────────────────────────────────────────────────────
    # 6. Confirm order - final step
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_CONFIRM_ORDER + "_FINAL"):
        try:
            order_id = int(callback.data.split(":")[-1])

        except (ValueError, IndexError):
            await callback.message.edit(
                "❌ خطا در دریافت اطلاعات سفارش.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = get_order_by_id(order_id)

        if not order:
            await callback.message.edit(
                "❌ سفارش مورد نظر یافت نشد.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Check status again before final confirmation.
        if order['status'] != 'pending':
            await callback.message.edit(
                f"❌ این سفارش قبلاً { 'تأیید' if order['status'] == 'confirmed' else 'لغو' } شده است.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Decrease product stock.
        if not decrease_product_stock(order_id):
            await callback.message.edit(
                "❌ **خطا در تأیید سفارش**\n\nموجودی برخی محصولات کافی نیست.\nلطفاً موجودی را بررسی کنید.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Update order status and archive confirmed order.
        if update_order_status(order_id, 'confirmed'):
            save_to_confirmed_tables(order_id)

            await callback.message.edit(
                f"✅ **سفارش با موفقیت تأیید شد!**\n\n"
                f"🆔 شناسه سفارش: {order_id}\n"
                f"👤 مشتری: {order['customer_name']}\n"
                f"💰 مبلغ: {order['total_price']:,} تومان\n\n"
                f"📦 موجودی محصولات کاهش یافت و در بایگانی مجزا ذخیره شد.",
                components=get_back_to_reports_keyboard()
            )

        else:
            await callback.message.edit(
                "❌ خطا در تأیید سفارش. لطفاً مجدداً تلاش کنید.",
                components=get_back_to_reports_keyboard()
            )

    # ──────────────────────────────────────────────────────────────────────
    # 7. Cancel order - first step
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER) and "_FINAL" not in callback.data and "_BACK" not in callback.data:
        try:
            order_id = int(callback.data.split(":")[-1])

        except (ValueError, IndexError):
            await callback.message.edit(
                "❌ خطا در دریافت اطلاعات سفارش.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = get_order_by_id(order_id)

        if not order:
            await callback.message.edit(
                "❌ سفارش مورد نظر یافت نشد.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Make sure the order is still pending.
        if order['status'] != 'pending':
            await callback.message.edit(
                f"❌ این سفارش قبلاً { 'تأیید' if order['status'] == 'confirmed' else 'لغو' } شده است.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Show final cancellation keyboard.
        keyboard, text = get_confirm_cancel_keyboard(order_id, 'cancel')
        order_text = format_order_text(order, 0, 1)

        await callback.message.edit(
            order_text + "\n\n" + text,
            components=keyboard
        )

    # ──────────────────────────────────────────────────────────────────────
    # 8. Cancel order - final step
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_NEW_ORDERS_CANCEL_ORDER + "_FINAL"):
        try:
            order_id = int(callback.data.split(":")[-1])

        except (ValueError, IndexError):
            await callback.message.edit(
                "❌ خطا در دریافت اطلاعات سفارش.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = get_order_by_id(order_id)

        if not order:
            await callback.message.edit(
                "❌ سفارش مورد نظر یافت نشد.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Check status again before final cancellation.
        if order['status'] != 'pending':
            await callback.message.edit(
                f"❌ این سفارش قبلاً { 'تأیید' if order['status'] == 'confirmed' else 'لغو' } شده است.",
                components=get_back_to_reports_keyboard()
            )
            return

        # Update order status to cancelled.
        if update_order_status(order_id, 'cancelled'):
            await callback.message.edit(
                f"❌ **سفارش با موفقیت لغو شد!**\n\n"
                f"🆔 شناسه سفارش: {order_id}\n"
                f"👤 مشتری: {order['customer_name']}\n"
                f"💰 مبلغ: {order['total_price']:,} تومان\n\n"
                f"⚠️ این عملیات غیرقابل بازگشت است.",
                components=get_back_to_reports_keyboard()
            )

        else:
            await callback.message.edit(
                "❌ خطا در لغو سفارش. لطفاً مجدداً تلاش کنید.",
                components=get_back_to_reports_keyboard()
            )

    # ──────────────────────────────────────────────────────────────────────
    # 9. Return from confirm/cancel confirmation
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.endswith("_BACK"):
        orders = get_orders_by_status('pending')

        if not orders:
            await callback.message.edit(
                "🆕 **سفارش‌های جدید**\n\nهیچ سفارش جدیدی وجود ندارد.",
                components=get_back_to_reports_keyboard()
            )
            return

        order = orders[0]
        text = format_order_text(order, 0, len(orders))
        keyboard = get_order_navigation_keyboard(order['id'], 0, len(orders), 'pending')

        await callback.message.edit(text, components=keyboard)

    # ──────────────────────────────────────────────────────────────────────
    # 10. Legacy details callback without order ID
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data == CB_SELLER_REPORTS_SHOW_DETAILS:
        await callback.message.edit(
            "📄 **جزئیات سفارش**\n\nاین بخش در حال تکمیل است.",
            components=get_back_to_reports_keyboard()
        )

    # ──────────────────────────────────────────────────────────────────────
    # 11. Show order details as PDF
    # ──────────────────────────────────────────────────────────────────────
    elif callback.data.startswith(CB_SELLER_REPORTS_SHOW_DETAILS):
        try:
            if ":" in callback.data:
                order_id = int(callback.data.split(":")[-1])

            else:
                await callback.message.edit(
                    "❌ شناسه سفارش برای نمایش جزئیات یافت نشد.",
                    components=get_back_to_reports_keyboard()
                )
                return

        except (ValueError, IndexError):
            await callback.message.edit(
                "❌ خطا در دریافت شناسه سفارش.",
                components=get_back_to_reports_keyboard()
            )
            return

        await send_order_details_pdf(callback, order_id)


# ══════════════════════════════════════════════════════════════════════════
# Back keyboard
# ══════════════════════════════════════════════════════════════════════════

def get_back_to_reports_keyboard():
    """
    Return the keyboard used for going back to the reports menu.
    """
    from keyboards.seller.reports.orders_report import main_menu_orders_report
    return main_menu_orders_report()