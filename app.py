import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
from fpdf import FPDF
from barcode import EAN13
from barcode.writer import ImageWriter

# إعداد المجلدات
if not os.path.exists("barcodes"): os.makedirs("barcodes")

# إعدادات الصفحة
st.set_page_config(page_title="غسق OS - برو", layout="wide")

# --- دالة الفاتورة الاحترافية ---
def generate_pro_pdf(item, qty, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102) # أزرق داكن
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(200, 20, "صيدلية غسق", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "الوصف", 1, 0, 'C', 1)
    pdf.cell(40, 10, "الكمية", 1, 0, 'C', 1)
    pdf.cell(50, 10, "السعر", 1, 1, 'C', 1)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, str(item), 1, 0, 'C')
    pdf.cell(40, 10, str(qty), 1, 0, 'C')
    pdf.cell(50, 10, f"{price * qty} ريال", 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- دالة الباركود ---
def gen_barcode(code_str):
    if len(code_str) != 12: code_str = code_str.ljust(12, '0')[:12] # EAN13 يحتاج 12 رقم
    ean = EAN13(code_str, writer=ImageWriter())
    file_path = f"barcodes/{code_str}"
    ean.save(file_path)
    return file_path + ".png"

# --- بقية المنطق البرمجي ---
# (استخدم نفس الدوال السابقة لإدارة قواعد البيانات ولكن مع إضافة زر الباركود في المخزون)
# ... [هنا تضع منطق init_db و process_sale من الكود السابق] ...
# (لم أكرره هنا لتوفير المساحة، لكن تأكد من وجوده في ملفك)

# --- الواجهة (نقطة البيع + الباركود) ---
page = st.sidebar.radio("القائمة", ["نقطة البيع", "المخزون"])

if page == "نقطة البيع":
    st.title("🛒 نقطة البيع (أدخل الباركود أو الاسم)")
    input_val = st.text_input("امسح الباركود أو اكتب الاسم:")
    qty = st.number_input("الكمية", 1)
    if st.button("إتمام البيع"):
        # منطق البيع المعتاد
        st.success("تم!")
        # زر الفاتورة الاحترافية
        pdf_data = generate_pro_pdf(input_val, qty, 50) # مثال للسعر
        st.download_button("📥 طباعة الفاتورة (PDF)", pdf_data, "invoice.pdf", "application/pdf")

elif page == "المخزون":
    st.title("📦 إدارة المخزون (توليد الباركود)")
    name = st.text_input("اسم الدواء")
    code = st.text_input("رقم الباركود (12 رقم):")
    if st.button("حفظ وتوليد الباركود"):
        img = gen_barcode(code)
        st.image(img)
        st.success("تم حفظ الباركود!")
