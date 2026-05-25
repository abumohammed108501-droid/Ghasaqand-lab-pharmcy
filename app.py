import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
from fpdf import FPDF
from barcode import EAN13
from barcode.writer import ImageWriter

# --- إعدادات النظام ---
st.set_page_config(page_title="غسق OS - النظام المتكامل", layout="wide")

# --- تهيئة المجلدات ---
if not os.path.exists("barcodes"): os.makedirs("barcodes")

# --- الأمان (تسجيل الدخول) ---
def check_password():
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pwd = st.sidebar.text_input("كلمة المرور:", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "1234":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("كلمة المرور خاطئة!")
        return False
    return True

# --- تهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, dept TEXT, item TEXT, qty REAL, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, price REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- الدوال البرمجية ---
def process_sale(item, qty):
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    c.execute("SELECT quantity, price FROM inventory WHERE item_name = ?", (item,))
    res = c.fetchone()
    if res and res[0] >= qty:
        c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?", (qty, item))
        c.execute("INSERT INTO sales (timestamp, dept, item, qty, price) VALUES (?, ?, ?, ?, ?)", 
                  (datetime.datetime.now().strftime("%Y-%m-%d"), "صيدلية", item, qty, res[1]))
        conn.commit(); conn.close()
        return True, res[1]
    conn.close(); return False, 0

def generate_pro_pdf(item, qty, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(200, 20, "صيدلية غسق - فاتورة", ln=True, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "الصنف", 1, 0, 'C', 1)
    pdf.cell(40, 10, "الكمية", 1, 0, 'C', 1)
    pdf.cell(50, 10, "الإجمالي", 1, 1, 'C', 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, str(item), 1, 0, 'C')
    pdf.cell(40, 10, str(qty), 1, 0, 'C')
    pdf.cell(50, 10, f"{price * qty} ريال", 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

def gen_barcode(code_str):
    if len(code_str) != 12: code_str = code_str.ljust(12, '0')[:12]
    ean = EAN13(code_str, writer=ImageWriter())
    file_path = f"barcodes/{code_str}"
    ean.save(file_path)
    return file_path + ".png"

# --- واجهة المستخدم ---
if check_password():
    st.sidebar.title("🛠️ لوحة تحكم غسق")
    page = st.sidebar.radio("الخدمات", ["المبيعات والتحليلات", "نقطة البيع", "إدارة المخزون"])

    if page == "المبيعات والتحليلات":
        st.title("📊 حركة المبيعات")
        df = pd.read_sql_query("SELECT * FROM sales", sqlite3.connect('ghasaq_os.db'))
        if not df.empty:
            st.bar_chart(df.groupby('timestamp')['price'].sum())
            st.dataframe(df, use_container_width=True)
        else: st.info("لا توجد مبيعات بعد")

    elif page == "نقطة البيع":
        st.title("🛒 نقطة البيع")
        item = st.text_input("اسم الصنف (أو امسح الباركود هنا)")
        qty = st.number_input("الكمية", 1)
        if st.button("إتمام البيع"):
            success, price = process_sale(item, qty)
            if success:
                st.success("تم البيع بنجاح!")
                st.download_button("📥 تحميل الفاتورة", generate_pro_pdf(item, qty, price), "invoice.pdf")
            else: st.error("خطأ: الصنف غير موجود أو الكمية غير كافية")

    elif page == "إدارة المخزون":
        st.title("📦 إدارة المخزون")
        # تنبيهات النواقص
        df_inv = pd.read_sql_query("SELECT * FROM inventory", sqlite3.connect('ghasaq_os.db'))
        if not df_inv.empty and not df_inv[df_inv['quantity'] < 5].empty:
            st.warning("⚠️ تنبيه: هذه الأصناف توشك على النفاد:")
            st.dataframe(df_inv[df_inv['quantity'] < 5])
        
        # إضافة صنف جديد
        with st.expander("إضافة صنف جديد / باركود"):
            name = st.text_input("اسم الدواء")
            qty = st.number_input("الكمية", 0.0)
            price = st.number_input("السعر")
            code = st.text_input("باركود (12 رقم):")
            if st.button("حفظ وتوليد باركود"):
                gen_barcode(code)
                st.success("تم!")
        
        st.dataframe(df_inv)
