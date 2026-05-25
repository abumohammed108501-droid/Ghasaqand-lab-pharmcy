import streamlit as st
import pandas as pd
import sqlite3
import datetime
from fpdf import FPDF
from barcode import EAN13
from barcode.writer import ImageWriter
import os

# --- إعدادات النظام ---
st.set_page_config(page_title="غسق OS - برو", layout="wide")
if not os.path.exists("barcodes"): os.makedirs("barcodes")

# --- تهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, item TEXT, qty REAL, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, price REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- دالة الفاتورة (مبسطة وسريعة) ---
def generate_pdf(item, qty, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "صيدلية غسق - الفاتورة", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"الصنف: {item}", ln=True)
    pdf.cell(200, 10, f"الكمية: {qty}", ln=True)
    pdf.cell(200, 10, f"الإجمالي: {qty * price} ريال", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- الواجهة ---
page = st.sidebar.radio("القائمة", ["نقطة البيع", "المخزون", "المبيعات"])

if page == "نقطة البيع":
    st.title("🛒 نقطة البيع")
    # المؤشر سيكون جاهزاً هنا لاستقبال بيانات الماسح الضوئي
    barcode_input = st.text_input("امسح الباركود:")
    qty = st.number_input("الكمية", 1)
    
    if st.button("إتمام البيع"):
        conn = sqlite3.connect('ghasaq_os.db')
        c = conn.cursor()
        c.execute("SELECT price FROM inventory WHERE id = ? OR item_name = ?", (barcode_input, barcode_input))
        res = c.fetchone()
        if res:
            st.success(f"تم البيع! السعر: {res[0]}")
            st.download_button("📥 طباعة الفاتورة", generate_pdf(barcode_input, qty, res[0]), "invoice.pdf")
        else:
            st.error("صنف غير موجود!")
        conn.close()

elif page == "المخزون":
    st.title("📦 إدارة المخزون")
    # ... (كود إضافة الأصناف المعتاد)
