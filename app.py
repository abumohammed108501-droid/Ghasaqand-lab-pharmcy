import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- إعدادات النظام ---
st.set_page_config(page_title="نظام غسق OS", layout="wide")

# --- تهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  dept TEXT, 
                  item TEXT, 
                  qty REAL, 
                  price REAL)''')
    conn.commit()
    conn.close()

# تنفيذ التهيئة
init_db()

# --- دالة إضافة عملية بيع ---
def add_sale(dept, item, qty, price):
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO sales (timestamp, dept, item, qty, price) VALUES (?, ?, ?, ?, ?)",
              (time, dept, item, qty, price))
    conn.commit()
    conn.close()

# --- دالة جلب المبيعات ---
def get_sales():
    conn = sqlite3.connect('ghasaq_os.db')
    df = pd.read_sql_query("SELECT * FROM sales ORDER BY id DESC", conn)
    conn.close()
    return df

# --- واجهة المستخدم ---
st.sidebar.title("🛠️ لوحة تحكم غسق")
page = st.sidebar.radio("الخدمات", ["📊 المبيعات اليومية", "🛒 نقطة البيع (POS)"])

if page == "📊 المبيعات اليومية":
    st.title("📊 حركة المبيعات اليومية")
    sales_df = get_sales()
    if not sales_df.empty:
        st.dataframe(sales_df, use_container_width=True)
        csv = sales_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير (CSV)", csv, "sales_report.csv", "text/csv")
    else:
        st.write("لا توجد مبيعات مسجلة حتى الآن.")

elif page == "🛒 نقطة البيع (POS)":
    st.title("🛒 نقطة البيع")
    tab1, tab2 = st.tabs(["💊 الصيدلية", "🧪 المعمل"])

    with tab1:
        with st.form("pharmacy_form", clear_on_submit=True):
            item = st.text_input("اسم الدواء")
            qty = st.number_input("الكمية", 1)
            price = st.number_input("السعر")
            if st.form_submit_button("إتمام البيع"):
                add_sale("صيدلية", item, qty, price)
                st.success("تم تسجيل البيع في قاعدة البيانات!")
                st.rerun()

    with tab2:
        with st.form("lab_form", clear_on_submit=True):
            test_name = st.text_input("اسم الفحص")
            price_lab = st.number_input("السعر")
            if st.form_submit_button("تسجيل الفحص"):
                add_sale("معمل", test_name, 1, price_lab)
                st.success("تم تسجيل الفحص في قاعدة البيانات!")
                st.rerun()
