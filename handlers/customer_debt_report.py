# Appearance of the PDF written with artificial intelligence

from keyboards.seller.account_book.main_menu_account_book import back_btn
import sqlite3
import os
import tempfile
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer)
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

# ══════════════════════════════════════════════════════════════════════════════
#  تنظیم فونت (از این فونت استفاده می‌شود: Vazir)
# ══════════════════════════════════════════════════════════════════════════════

def load_font() -> str:
    """بارگذاری فونت Vazir"""
    font_paths = [
        'Vazir.ttf',
        'Vazir-Bold.ttf', 
        'fonts/Vazir.ttf',
        'fonts/Vazir-Bold.ttf',
        '../Vazir.ttf']
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

# ══════════════════════════════════════════════════════════════════════════════
#  توابع کمکی
# ══════════════════════════════════════════════════════════════════════════════

def fa(text: str) -> str:
    """تبدیل متن فارسی به راست‌چین"""
    if text is None:
        text = ""
    text = str(text)
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

def fmt_price(amount: int) -> str:
    """فرمت قیمت با کاما"""
    return f"{amount:,}"

def fmt_date(raw) -> str:
    """فرمت تاریخ"""
    if not raw:
        return "-"
    try:
        s = str(raw)
        return s.split()[0] if ' ' in s else s[:10]
    except:
        return "-"

# ══════════════════════════════════════════════════════════════════════════════
#  توابع دیتابیس
# ══════════════════════════════════════════════════════════════════════════════

def get_all_customers_with_debt() -> list:
    """گرفتن همه مشتریان بدهکار"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            c.id,
            c.name,
            c.phone,
            COALESCE(SUM(t.amount), 0) AS total_debt
        FROM customers c
        LEFT JOIN transactions t ON c.id = t.customer_id
        GROUP BY c.id, c.name, c.phone
        HAVING total_debt > 0
        ORDER BY total_debt DESC
    """)
    customers = [dict(r) for r in cur.fetchall()]
    
    for cust in customers:
        cur.execute("""
            SELECT id, amount, reason, created_at
            FROM transactions
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (cust['id'],))
        cust['transactions'] = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return customers

def get_total_system_debt() -> int:
    """جمع کل بدهی سیستم"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
    total = cur.fetchone()[0]
    conn.close()
    return total

# ══════════════════════════════════════════════════════════════════════════════
#  تولید PDF (نسخه نهایی با ظاهر حرفه‌ای)
# ══════════════════════════════════════════════════════════════════════════════

async def generate_customers_debt_pdf() -> str:
    """تولید فایل PDF"""
    customers = get_all_customers_with_debt()
    
    if not customers:
        return None
    
    FONT = load_font()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  استایل‌ها (همه با فونت بزرگ و بولد)
    # ══════════════════════════════════════════════════════════════════════════
    
    # عنوان اصلی سند
    style_title = ParagraphStyle(
        name='Title',
        fontName=FONT,
        fontSize=28,
        alignment=1,  # وسط
        spaceAfter=15,
        leading=38,
        bold=True)
    
    # زیرعنوان (تاریخ)
    style_subtitle = ParagraphStyle(
        name='Subtitle',
        fontName=FONT,
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=25,
        leading=20,
        bold=False)
    
    # نام مشتری (بزرگ و پررنگ)
    style_customer_name = ParagraphStyle(
        name='CustomerName',
        fontName=FONT,
        fontSize=20,
        alignment=2,  # راست
        spaceAfter=12,
        leading=30,
        bold=True,
        textColor=colors.HexColor('#1a237e'))
    
    # شماره مشتری (آیتم جداگانه)
    style_customer_number = ParagraphStyle(
        name='CustomerNumber',
        fontName=FONT,
        fontSize=14,
        alignment=2,  # راست
        spaceAfter=6,
        leading=22,
        bold=True,
        textColor=colors.HexColor('#555555'))
    
    # شماره تماس (آیتم جداگانه)
    style_customer_phone = ParagraphStyle(
        name='CustomerPhone',
        fontName=FONT,
        fontSize=14,
        alignment=2,  # راست
        spaceAfter=6,
        leading=22,
        bold=False,
        textColor=colors.HexColor('#555555'))
    
    # شناسه (آیتم جداگانه)
    style_customer_id = ParagraphStyle(
        name='CustomerId',
        fontName=FONT,
        fontSize=14,
        alignment=2,  # راست
        spaceAfter=6,
        leading=22,
        bold=False,
        textColor=colors.HexColor('#555555'))
    
    # مجموع بدهی (بزرگ، قرمز، پررنگ)
    style_debt_label = ParagraphStyle(
        name='DebtLabel',
        fontName=FONT,
        fontSize=15,
        alignment=2,  # راست
        spaceAfter=5,
        leading=24,
        bold=True,
        textColor=colors.HexColor('#333333'))
    
    style_debt_value = ParagraphStyle(
        name='DebtValue',
        fontName=FONT,
        fontSize=18,
        alignment=2,  # راست
        spaceAfter=20,
        leading=28,
        bold=True,
        textColor=colors.HexColor('#d32f2f'))
    
    # هدر جدول
    style_th = ParagraphStyle(
        name='TableHeader',
        fontName=FONT,
        fontSize=14,
        alignment=1,  # وسط
        textColor=colors.white,
        leading=24,
        bold=True)
    
    # سلول جدول
    style_td = ParagraphStyle(
        name='TableCell',
        fontName=FONT,
        fontSize=13,
        alignment=1,
        leading=22,
        bold=False)
    
    # مبلغ بدهی در جدول (قرمز)
    style_amount_debt = ParagraphStyle(
        name='AmountDebt',
        fontName=FONT,
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#d32f2f'),
        leading=22,
        bold=True)
    
    # مبلغ پرداخت در جدول (سبز)
    style_amount_credit = ParagraphStyle(
        name='AmountCredit',
        fontName=FONT,
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor('#2e7d32'),
        leading=22,
        bold=True)
    
    # تاریخ در جدول
    style_td_date = ParagraphStyle(
        name='TdDate',
        fontName=FONT,
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        leading=22,
        bold=False)
    
    # متن خالی/هیچ
    style_empty = ParagraphStyle(
        name='Empty',
        fontName=FONT,
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor('#999999'),
        leading=22,
        bold=False)
    
    # عنوان خلاصه
    style_summary_title = ParagraphStyle(
        name='SummaryTitle',
        fontName=FONT,
        fontSize=18,
        alignment=1,
        spaceAfter=15,
        leading=28,
        bold=True,
        textColor=colors.HexColor('#1a237e'))
    
    # جمع کل مقدار (بزرگ)
    style_summary_value = ParagraphStyle(
        name='SummaryValue',
        fontName=FONT,
        fontSize=22,
        alignment=1,
        spaceAfter=5,
        leading=34,
        bold=True,
        textColor=colors.HexColor('#d32f2f'))
    
    # متن معمولی خلاصه
    style_summary_text = ParagraphStyle(
        name='SummaryText',
        fontName=FONT,
        fontSize=15,
        alignment=1,
        leading=24,
        bold=False)
    
    # جداکننده
    style_separator = ParagraphStyle(
        name='Separator',
        fontName=FONT,
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#cccccc'),
        leading=16,
        bold=False)
    
    # ══════════════════════════════════════════════════════════════════════════
    #  ساخت PDF
    # ══════════════════════════════════════════════════════════════════════════
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        filepath = tmp.name
    
    elements = []
    
    # ──────────────────────────────────────────────────────────────────────────
    #  هدر سند
    # ──────────────────────────────────────────────────────────────────────────
    elements.append(Paragraph(fa("گزارش دفترچه حساب مشتریان"), style_title))
    elements.append(Paragraph(fa(f"تاریخ چاپ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), style_subtitle))
    
    # ──────────────────────────────────────────────────────────────────────────
    #  حلقه مشتریان
    # ──────────────────────────────────────────────────────────────────────────
    for idx, cust in enumerate(customers, 1):
        
        # شماره و نام مشتری
        elements.append(Paragraph(fa(f"مشتری شماره {idx} : {cust['name']}"), style_customer_name))
        
        # شناسه
        elements.append(Paragraph(fa(f"شناسه مشتری : {cust['id']}"), style_customer_id))
        
        # شماره تماس
        elements.append(Paragraph(fa(f"شماره تماس : {cust['phone']}"), style_customer_phone))
        
        # مجموع بدهی
        elements.append(Paragraph(fa("مجموع بدهی :"), style_debt_label))
        elements.append(Paragraph(fa(f"{fmt_price(cust['total_debt'])} تومان"), style_debt_value))
        
        elements.append(Spacer(1, 10))
        
        # ──────────────────────────────────────────────────────────────────────
        #  جدول تراکنش‌ها
        # ──────────────────────────────────────────────────────────────────────
        if cust['transactions']:
            
            # هدر جدول
            headers = [
                Paragraph(fa("تاریخ"), style_th),
                Paragraph(fa("علت / توضیحات"), style_th),
                Paragraph(fa("مبلغ (تومان)"), style_th),
            ]
            
            rows = [headers]
            
            for trans in cust['transactions']:
                amt = trans['amount']
                reason = trans['reason'] if trans['reason'] else "———"
                date_str = fmt_date(trans['created_at'])
                
                if amt > 0:
                    amt_text = f"+ {fmt_price(amt)}"
                    amt_style = style_amount_debt
                else:
                    amt_text = f"- {fmt_price(abs(amt))}"
                    amt_style = style_amount_credit
                
                rows.append([
                    Paragraph(fa(date_str), style_td_date),
                    Paragraph(fa(reason), style_td),
                    Paragraph(fa(amt_text), amt_style),
                ])
            
            # عرض ستون‌ها
            col_widths = [120, 330, 150]
            
            table = Table(rows, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), FONT),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph(fa("◆ ◆ ◆  هیچ تراکنشی ثبت نشده است  ◆ ◆ ◆"), style_empty))
        
        # خط جداکننده بعد از هر مشتری (به جز آخرین مشتری)
        if idx < len(customers):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(fa("_________________________________________________________________"), style_separator))
            elements.append(Spacer(1, 10))    
    # ──────────────────────────────────────────────────────────────────────────
    #  جمع کل نهایی
    # ──────────────────────────────────────────────────────────────────────────
    total_debt = get_total_system_debt()
    total_customers = len(customers)
    
    elements.append(Spacer(1, 25))
    elements.append(Paragraph(fa("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"), style_separator))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(fa("خلاصه نهایی گزارش"), style_summary_title))
    elements.append(Paragraph(fa(f"تعداد مشتریان بدهکار : {total_customers} نفر"), style_summary_text))
    elements.append(Paragraph(fa(f"جمع کل بدهی سیستم : {fmt_price(total_debt)} تومان"), style_summary_value))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  فوتر (شماره صفحات)
    # ══════════════════════════════════════════════════════════════════════════
    def add_footer(canvas, doc):
        page = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont(FONT, 10)
        canvas.setFillColor(colors.HexColor('#999999'))
        
        # خط جداکننده فوتر
        canvas.setStrokeColor(colors.HexColor('#dddddd'))
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.8*cm, landscape(A4)[0] - 2*cm, 1.8*cm)
        
        # شماره صفحه در سمت راست
        canvas.drawRightString(landscape(A4)[0] - 2*cm, 1.2*cm, fa(f"صفحه {page}"))
        
        # متن در سمت چپ
        canvas.drawString(2*cm, 1.2*cm, fa("گزارش دفترچه حساب مشتریان"))
        
        canvas.restoreState()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  ساخت نهایی PDF
    # ══════════════════════════════════════════════════════════════════════════
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=2*cm,
        bottomMargin=2.2*cm,
    )
    
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
#  ارسال به ربات
# ══════════════════════════════════════════════════════════════════════════════

async def send_customers_debt_pdf(callback):
    """ارسال PDF به فروشنده"""
    await callback.message.edit("⏳ در حال تولید فایل PDF گزارش مشتریان، لطفاً صبر کنید...")
    
    try:
        filepath = await generate_customers_debt_pdf()
        
        if filepath and os.path.exists(filepath):
            fname = f"customers_debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filepath, 'rb') as f:
                await callback.bot.send_document(
                    callback.message.chat.id,
                    InputFile(f, file_name=fname),
                    caption=f"📊 گزارش دفترچه حساب مشتریان\n📅 تاریخ: {datetime.now().strftime('%Y/%m/%d')}\n\n✅ این گزارش شامل تمام مشتریانی است که بدهی دارند."
                )
            os.remove(filepath)
            await callback.message.edit("✅ فایل PDF با موفقیت ارسال شد.", components=back_btn())
        else:
            await callback.message.edit("❌ هیچ مشتری بدهکاری در سیستم وجود ندارد!", components=back_btn())
            
    except Exception as e:
        print(f"[PDF Error] {e}")
        await callback.message.edit(f"❌ خطا در تولید PDF: {str(e)}", components=back_btn())