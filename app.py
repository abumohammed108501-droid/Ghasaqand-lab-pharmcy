import streamlit as st
import pandas as pd
import sqlite3
import datetime
from fpdf import FPDF

# --- إعدادات النظام ---
st.set_page_config(page_title="غسق OS - النظام الاحترافي", layout="wide")

# --- الأمان (تسجيل الدخول) ---
def check_password():
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        pwd = st.sidebar.text_input("أدخل كلمة المرور:", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "1234": # غير هذه الكلمة كما تشاء
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("كلمة المرور خاطئة!")
        return False
    return True

# --- تهيئة النظام ---
init_db = lambda: [c.execute(f"CREATE TABLE IF NOT EXISTS {t}") for t in ["sales (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, dept TEXT, item TEXT, qty REAL, price REAL)", "inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, price REAL)"]]
conn = sqlite3.connect('ghasaq_os.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, dept TEXT, item TEXT, qty REAL, price REAL)")
c.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, price REAL)")
conn.commit(); conn.close()

# --- الدوال البرمجية ---
def process_sale(item, qty):
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    c.execute("SELECT quantity, price FROM inventory WHERE item_name = ?", (item,))
    res = c.fetchone()
    if res and res[0] >= qty:
        c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?", (qty, item))
        c.execute("INSERT INTO sales (timestamp, dept, item, qty, price) VALUES (?, ?, ?, ?, ?)", (datetime.datetime.now().strftime("%Y-%m-%d"), "صيدلية", item, qty, res[1]))
        conn.commit(); conn.close()
        return True, res[1]
    conn.close(); return False, 0

def generate_pdf(item, qty, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "صيدلية غسق - فاتورة", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"الصنف: {item} | الكمية: {qty}", ln=True)
    pdf.cell(200, 10, f"الإجمالي: {price * qty} ريال", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- واجهة المستخدم ---
if check_password():
    page = st.sidebar.radio("الخدمات", ["المبيعات والتحليلات", "نقطة البيع", "إدارة المخزون"])

    if page == "المبيعات والتحليلات":
        st.title("📊 المبيعات والتحليلات")
        df = pd.read_sql_query("SELECT * FROM sales", sqlite3.connect('ghasaq_os.db'))
        if not df.empty:
            # الرسم البياني
            daily_sales = df.groupby('timestamp')['price'].sum()
            st.bar_chart(daily_sales)
            st.dataframe(df, use_container_width=True)
        else: st.info("لا توجد مبيعات بعد")

    elif page == "نقطة البيع":
        st.title("🛒 نقطة البيع")
        item = st.text_input("اسم الصنف")
        qty = st.number_input("الكمية", 1)
        if st.button("إتمام البيع"):
            success, price = process_sale(item, qty)
            if success:
                st.success("تم البيع بنجاح!")
                st.download_button("📥 تحميل الفاتورة", generate_pdf(item, qty, price), "invoice.pdf")
            else: st.error("الصنف غير متوفر أو غير موجود")

    elif page == "إدارة المخزون":
        st.title("📦 إدارة المخزون")
        # تنبيهات النواقص
        df_inv = pd.read_sql_query("SELECT * FROM inventory", sqlite3.connect('ghasaq_os.db'))
        low_stock = df_inv[df_inv['quantity'] < 5]
        if not low_stock.empty:
            st.warning("⚠️ تنبيه: هذه الأصناف أوشكت على النفاد:")
            st.dataframe(low_stock)
        
        st.subheader("المخزون الحالي")
        st.dataframe(df_inv)
