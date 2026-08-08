"""
Handler for generating and sending PDF report of one order details.
"""

import sqlite3
import os
import tempfile
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import arabic_reshaper
from bidi.algorithm import get_display
from bale import InputFile

from keyboards.seller.reports.orders_report import main_menu_orders_report


DB_NAME = "database.db"


def load_font() -> str:
    """
    Load Vazir font.
    """
    font_paths = [
        'Vazir.ttf',
        'Vazir-Bold.ttf',
        'fonts/Vazir.ttf',
        'fonts/Vazir-Bold.ttf',
        '../Vazir.ttf'
    ]

    for path in font_paths:
        try:
            pdfmetrics.registerFont(TTFont('Vazir', path))
            print(f"Font Vazir successfully loaded from {path}")
            return 'Vazir'
        except Exception:
            continue

    print("Font Vazir not found! Please place Vazir.ttf file in project directory.")
    print("Current directory:", os.getcwd())
    return 'Helvetica'


def fa(text: str) -> str:
    """
    Fix Persian/Arabic text direction for PDF.
    """
    if text is None:
        text = ""

    text = str(text)

    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def fmt_price(amount) -> str:
    """
    Format price with comma separator.
    """
    try:
        return f"{int(amount):,}"
    except Exception:
        return "0"


def get_status_text(status: str) -> str:
    """
    Convert order status to Persian text.
    """
    statuses = {
        'pending': 'در انتظار تأیید',
        'confirmed': 'تأیید شده',
        'cancelled': 'لغو شده'
    }
    return statuses.get(status, status or "نامشخص")


def get_order_for_report(order_id: int):
    """
    Get order data.

    First tries main orders table.
    If not found, tries confirmed_orders archive table.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # 1) Try normal orders table
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
                cancelled_at,
                'orders' AS source_table
            FROM orders
            WHERE id = ?
        """, (order_id,))

        row = cur.fetchone()
        if row:
            data = dict(row)
            data['items_ref_id'] = order_id
            return data

        # 2) Try confirmed archive table
        cur.execute("""
            SELECT
                id AS confirmed_id,
                original_order_id AS id,
                customer_name,
                customer_phone,
                customer_address,
                customer_note,
                total_price,
                confirmed_at,
                'confirmed_orders' AS source_table
            FROM confirmed_orders
            WHERE original_order_id = ?
            ORDER BY confirmed_at DESC
            LIMIT 1
        """, (order_id,))

        row = cur.fetchone()
        if row:
            data = dict(row)
            data['status'] = 'confirmed'
            data['created_at'] = data.get('confirmed_at')
            data['cancelled_at'] = None
            data['items_ref_id'] = data.get('confirmed_id')
            return data

        return None

    finally:
        conn.close()


def get_order_items_for_report(order: dict):
    """
    Get order items.

    If order is from orders table:
        order_items JOIN products

    If order is from confirmed_orders archive:
        confirmed_order_items JOIN products
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        if order.get('source_table') == 'confirmed_orders':
            cur.execute("""
                SELECT
                    coi.id,
                    coi.product_id,
                    coi.quantity,
                    coi.price,
                    COALESCE(p.name, 'محصول حذف شده') AS product_name,
                    COALESCE(p.brand, '-') AS product_brand
                FROM confirmed_order_items coi
                LEFT JOIN products p ON coi.product_id = p.id
                WHERE coi.confirmed_order_id = ?
                ORDER BY coi.id
            """, (order.get('items_ref_id'),))
        else:
            cur.execute("""
                SELECT
                    oi.id,
                    oi.product_id,
                    oi.quantity,
                    oi.price,
                    COALESCE(p.name, 'محصول حذف شده') AS product_name,
                    COALESCE(p.brand, '-') AS product_brand
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
                ORDER BY oi.id
            """, (order.get('items_ref_id'),))

        return [dict(row) for row in cur.fetchall()]

    finally:
        conn.close()


async def generate_order_details_pdf(order_id: int) -> str:
    """
    Generate PDF report for one order.

    Returns:
        str: path of generated PDF file
    """
    order = get_order_for_report(order_id)
    if not order:
        return None

    items = get_order_items_for_report(order)

    FONT = load_font()

    # Styles
    style_title = ParagraphStyle(
        name='Title',
        fontName=FONT,
        fontSize=26,
        alignment=1,
        spaceAfter=12,
        leading=36,
        textColor=colors.HexColor('#1a237e')
    )

    style_subtitle = ParagraphStyle(
        name='Subtitle',
        fontName=FONT,
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=25,
        leading=20
    )

    style_info_label = ParagraphStyle(
        name='InfoLabel',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        leading=20,
        textColor=colors.HexColor('#2c3e50')
    )

    style_info_value = ParagraphStyle(
        name='InfoValue',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        leading=20
    )

    style_th = ParagraphStyle(
        name='TableHeader',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        textColor=colors.white,
        leading=20
    )

    style_td = ParagraphStyle(
        name='TableCell',
        fontName=FONT,
        fontSize=11,
        alignment=1,
        leading=18
    )

    style_td_price = ParagraphStyle(
        name='TableCellPrice',
        fontName=FONT,
        fontSize=11,
        alignment=1,
        textColor=colors.HexColor('#2e7d32'),
        leading=18
    )

    style_summary_title = ParagraphStyle(
        name='SummaryTitle',
        fontName=FONT,
        fontSize=18,
        alignment=1,
        spaceAfter=15,
        leading=28,
        textColor=colors.HexColor('#1a237e')
    )

    style_summary_text = ParagraphStyle(
        name='SummaryText',
        fontName=FONT,
        fontSize=14,
        alignment=1,
        leading=24
    )

    style_summary_value = ParagraphStyle(
        name='SummaryValue',
        fontName=FONT,
        fontSize=20,
        alignment=1,
        spaceAfter=5,
        leading=32,
        textColor=colors.HexColor('#d32f2f')
    )

    # Create temp PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        filepath = tmp.name

    elements = []

    # Header
    elements.append(Paragraph(fa("جزئیات سفارش"), style_title))
    elements.append(
        Paragraph(
            fa(f"تاریخ چاپ گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            style_subtitle
        )
    )

    # Order info table
    status = order.get('status', 'pending')

    info_rows = [
        [
            Paragraph(fa("شناسه سفارش"), style_info_label),
            Paragraph(fa(str(order.get('id', order_id))), style_info_value)
        ],
        [
            Paragraph(fa("نام مشتری"), style_info_label),
            Paragraph(fa(order.get('customer_name') or "-"), style_info_value)
        ],
        [
            Paragraph(fa("شماره تلفن"), style_info_label),
            Paragraph(fa(order.get('customer_phone') or "-"), style_info_value)
        ],
        [
            Paragraph(fa("آدرس"), style_info_label),
            Paragraph(fa(order.get('customer_address') or "-"), style_info_value)
        ],
        [
            Paragraph(fa("یادداشت مشتری"), style_info_label),
            Paragraph(fa(order.get('customer_note') or "-"), style_info_value)
        ],
        [
            Paragraph(fa("وضعیت سفارش"), style_info_label),
            Paragraph(fa(get_status_text(status)), style_info_value)
        ],
        [
            Paragraph(fa("تاریخ ثبت سفارش"), style_info_label),
            Paragraph(fa(order.get('created_at') or "-"), style_info_value)
        ],
    ]

    if order.get('confirmed_at'):
        info_rows.append([
            Paragraph(fa("تاریخ تأیید سفارش"), style_info_label),
            Paragraph(fa(order.get('confirmed_at')), style_info_value)
        ])

    if order.get('cancelled_at'):
        info_rows.append([
            Paragraph(fa("تاریخ لغو سفارش"), style_info_label),
            Paragraph(fa(order.get('cancelled_at')), style_info_value)
        ])

    info_rows.append([
        Paragraph(fa("مبلغ کل سفارش"), style_info_label),
        Paragraph(
            fa(f"{fmt_price(order.get('total_price', 0))} تومان"),
            style_info_value
        )
    ])

    info_table = Table(info_rows, colWidths=[190, 560])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f3f4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 25))

    # Order items table
    elements.append(Paragraph(fa("اقلام سفارش"), style_summary_title))

    total_quantity = 0
    calculated_total = 0

    if items:
        headers = [
            Paragraph(fa("ردیف"), style_th),
            Paragraph(fa("نام محصول"), style_th),
            Paragraph(fa("برند"), style_th),
            Paragraph(fa("تعداد"), style_th),
            Paragraph(fa("قیمت واحد (تومان)"), style_th),
            Paragraph(fa("جمع ردیف (تومان)"), style_th),
        ]

        rows = [headers]

        for idx, item in enumerate(items, 1):
            quantity = int(item.get('quantity') or 0)
            price = int(item.get('price') or 0)
            row_total = quantity * price

            total_quantity += quantity
            calculated_total += row_total

            rows.append([
                Paragraph(fa(str(idx)), style_td),
                Paragraph(fa(item.get('product_name') or "-"), style_td),
                Paragraph(fa(item.get('product_brand') or "-"), style_td),
                Paragraph(fa(str(quantity)), style_td),
                Paragraph(fa(fmt_price(price)), style_td_price),
                Paragraph(fa(fmt_price(row_total)), style_td_price),
            ])

        col_widths = [55, 235, 130, 90, 120, 120]

        items_table = Table(rows, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(items_table)

    else:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(fa("اقلام سفارش یافت نشد."), style_td))

    # Summary
    final_total = int(order.get('total_price') or calculated_total or 0)

    elements.append(Spacer(1, 25))
    elements.append(Paragraph(fa("خلاصه سفارش"), style_summary_title))
    elements.append(
        Paragraph(
            fa(f"تعداد اقلام سفارش: {len(items)} عدد"),
            style_summary_text
        )
    )
    elements.append(
        Paragraph(
            fa(f"تعداد کل محصولات: {total_quantity} عدد"),
            style_summary_text
        )
    )
    elements.append(
        Paragraph(
            fa(f"ارزش کل سفارش: {fmt_price(final_total)} تومان"),
            style_summary_value
        )
    )

    # Footer
    def add_footer(canvas, doc):
        page = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont(FONT, 10)
        canvas.setFillColor(colors.HexColor('#999999'))
        canvas.setStrokeColor(colors.HexColor('#dddddd'))
        canvas.setLineWidth(0.5)

        canvas.line(
            2 * cm,
            1.8 * cm,
            landscape(A4)[0] - 2 * cm,
            1.8 * cm
        )

        canvas.drawRightString(
            landscape(A4)[0] - 2 * cm,
            1.2 * cm,
            fa(f"صفحه {page}")
        )

        canvas.drawString(
            2 * cm,
            1.2 * cm,
            fa("جزئیات سفارش")
        )

        canvas.restoreState()

    # Build PDF
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
    )

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

    return filepath


async def send_order_details_pdf(callback, order_id: int):
    """
    Send order details PDF to chat.
    """
    await callback.message.edit("⏳ در حال تولید فایل PDF جزئیات سفارش، لطفاً صبر کنید...")

    try:
        filepath = await generate_order_details_pdf(order_id)

        if filepath and os.path.exists(filepath):
            fname = f"order_details_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            with open(filepath, 'rb') as f:
                await callback.bot.send_document(
                    callback.message.chat.id,
                    InputFile(f, file_name=fname),
                    caption=(
                        f"📄 جزئیات سفارش #{order_id}\n"
                        f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
                    )
                )

            os.remove(filepath)

            await callback.message.edit(
                "✅ فایل PDF جزئیات سفارش با موفقیت ارسال شد.",
                components=main_menu_orders_report()
            )

        else:
            await callback.message.edit(
                "❌ سفارشی برای نمایش یافت نشد.",
                components=main_menu_orders_report()
            )

    except Exception as e:
        print(f"[Order Details PDF Error] {e}")
        await callback.message.edit(
            f"❌ خطا در تولید PDF جزئیات سفارش: {str(e)}",
            components=main_menu_orders_report()
        )
