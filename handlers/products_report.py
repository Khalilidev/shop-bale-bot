# This section was written with the help of DeepSeek-V3.
"""
Handler for generating and sending PDF report of all products.
"""
from keyboards.seller.account_book.main_menu_account_book import back_btn, back_btn_to_seller_menu
import sqlite3
import os
import tempfile
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import arabic_reshaper
from bidi.algorithm import get_display
from bale import InputFile
DB_NAME = "database.db"
def load_font() -> str:
    """
    load the vazir font.
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
        except:
            continue

    print("Font Vazir not found! Please place Vazir.ttf file in project directory.")
    print("Current directory:", os.getcwd())
    return 'Helvetica'


def fa(text: str) -> str:
    """
    Shift the persian font to right.
    """
    if text is None:
        text = ""
    text = str(text)
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text
def fmt_price(amount: int) -> str:
    """
    Price format with ",".
    """
    return f"{amount:,}"
def get_all_products() -> list:
    """
    Get products from Database.
    Args:
        None
    Returns:
        list: List of all products.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            id,
            name,
            brand,
            category,
            description,
            price,
            stock_quantity as stock
        FROM products
        ORDER BY id
    """)
    
    products = [dict(row) for row in cur.fetchall()]
    conn.close()
    return products
def get_total_products_value() -> int:
    """
    Calculating the total value of inventory.
    Args:
        None
    Returns:    
        int: total of value.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT SUM(price * stock_quantity) FROM products")
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0
async def generate_products_report_pdf() -> str:
    """
    Generate PDF report of all products.
    Args:
        None
    Returns:
        str: path of the generated pdf.
    """
    products = get_all_products()
    
    if not products:
        return None
    
    FONT = load_font()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  Styles
    # ══════════════════════════════════════════════════════════════════════════
    
    style_title = ParagraphStyle(
        name='Title',
        fontName=FONT,
        fontSize=28,
        alignment=1,
        spaceAfter=15,
        leading=38,
        bold=True)
    
    style_subtitle = ParagraphStyle(
        name='Subtitle',
        fontName=FONT,
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=25,
        leading=20,
        bold=False)
    
    style_th = ParagraphStyle(
        name='TableHeader',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        textColor=colors.white,
        leading=20,
        bold=True)
    
    style_td = ParagraphStyle(
        name='TableCell',
        fontName=FONT,
        fontSize=11,
        alignment=1,
        leading=18,
        bold=False)
    
    style_td_left = ParagraphStyle(
        name='TableCellLeft',
        fontName=FONT,
        fontSize=11,
        alignment=0,
        leading=18,
        bold=False)
    
    style_td_price = ParagraphStyle(
        name='TableCellPrice',
        fontName=FONT,
        fontSize=11,
        alignment=1,
        textColor=colors.HexColor('#2e7d32'),
        leading=18,
        bold=True)
    
    style_td_stock = ParagraphStyle(
        name='TableCellStock',
        fontName=FONT,
        fontSize=11,
        alignment=1,
        textColor=colors.HexColor('#1565c0'),
        leading=18,
        bold=True)
    
    style_summary_title = ParagraphStyle(
        name='SummaryTitle',
        fontName=FONT,
        fontSize=18,
        alignment=1,
        spaceAfter=15,
        leading=28,
        bold=True,
        textColor=colors.HexColor('#1a237e'))
    
    style_summary_value = ParagraphStyle(
        name='SummaryValue',
        fontName=FONT,
        fontSize=22,
        alignment=1,
        spaceAfter=5,
        leading=34,
        bold=True,
        textColor=colors.HexColor('#d32f2f'))
    
    style_summary_text = ParagraphStyle(
        name='SummaryText',
        fontName=FONT,
        fontSize=15,
        alignment=1,
        leading=24,
        bold=False)
    
    style_separator = ParagraphStyle(
        name='Separator',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#cccccc'),
        leading=16,
        bold=False)
    
    # ══════════════════════════════════════════════════════════════════════════
    #  Create PDF
    # ══════════════════════════════════════════════════════════════════════════
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        filepath = tmp.name
    
    elements = []
    
    # Header
    elements.append(Paragraph(fa("گزارش لیست محصولات"), style_title))
    elements.append(Paragraph(fa(f"تاریخ چاپ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), style_subtitle))
    
    # ──────────────────────────────────────────────────────────────────────────
    #  Products table
    # ──────────────────────────────────────────────────────────────────────────
    
    # Table header
    headers = [
        Paragraph(fa("ردیف"), style_th),
        Paragraph(fa("شناسه"), style_th),
        Paragraph(fa("نام محصول"), style_th),
        Paragraph(fa("برند"), style_th),
        Paragraph(fa("دسته‌بندی"), style_th),
        Paragraph(fa("قیمت (تومان)"), style_th),
        Paragraph(fa("موجودی"), style_th),]

    rows = [headers]

    for idx, product in enumerate(products, 1):
        rows.append([
            Paragraph(fa(str(idx)), style_td),
            Paragraph(fa(str(product['id'])), style_td),
            Paragraph(fa(product['name']), style_td),
            Paragraph(fa(product['brand']), style_td),
            Paragraph(fa(product.get('category', 'بدون دسته‌بندی')), style_td),
            Paragraph(fa(fmt_price(product['price'])), style_td_price),
            Paragraph(fa(str(product['stock'])), style_td_stock),
        ])

    col_widths = [60, 70, 200, 130, 140, 130, 80]  # تغییر عرض ستون‌ها
        
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),]))
    
    elements.append(table)
    
    # ──────────────────────────────────────────────────────────────────────────
    #  Total
    # ──────────────────────────────────────────────────────────────────────────
    total_products = len(products)
    total_value = get_total_products_value()
    
    elements.append(Spacer(1, 25))
    elements.append(Paragraph(fa("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"), style_separator))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(fa("خلاصه گزارش محصولات"), style_summary_title))
    elements.append(Paragraph(fa(f"تعداد کل محصولات : {total_products} عدد"), style_summary_text))
    elements.append(Paragraph(fa(f"ارزش کل موجودی : {fmt_price(total_value)} تومان"), style_summary_value))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  Footer
    # ══════════════════════════════════════════════════════════════════════════
    def add_footer(canvas, doc):
        page = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont(FONT, 10)
        canvas.setFillColor(colors.HexColor('#999999'))
        canvas.setStrokeColor(colors.HexColor('#dddddd'))
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.8*cm, landscape(A4)[0] - 2*cm, 1.8*cm)
        canvas.drawRightString(landscape(A4)[0] - 2*cm, 1.2*cm, fa(f"صفحه {page}"))
        canvas.drawString(2*cm, 1.2*cm, fa("گزارش لیست محصولات"))
        canvas.restoreState()
    # ══════════════════════════════════════════════════════════════════════════
    #  Generate PDF
    # ══════════════════════════════════════════════════════════════════════════
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2.2*cm,)
    
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    
    return filepath

async def send_products_report_pdf(callback):
    """"
    Send report of products.
    """
    await callback.message.edit("⏳ در حال تولید فایل PDF گزارش محصولات، لطفاً صبر کنید...")
    
    try:
        filepath = await generate_products_report_pdf()
        
        if filepath and os.path.exists(filepath):
            fname = f"products_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filepath, 'rb') as f:
                await callback.bot.send_document(
                    callback.message.chat.id,
                    InputFile(f, file_name=fname),
                    caption=f"📊 گزارش لیست محصولات\n📅 تاریخ: {datetime.now().strftime('%Y/%m/%d')}\n\n✅ این گزارش شامل تمام محصولات موجود است.")
            os.remove(filepath)
            await callback.message.edit("✅ فایل PDF با موفقیت ارسال شد.", components=back_btn_to_seller_menu())
        else:
            await callback.message.edit("❌ هیچ محصولی در سیستم وجود ندارد!", components=back_btn_to_seller_menu())
            
    except Exception as e:
        print(f"[PDF Error] {e}")
        await callback.message.edit(f"❌ خطا در تولید PDF: {str(e)}", components=back_btn_to_seller_menu())