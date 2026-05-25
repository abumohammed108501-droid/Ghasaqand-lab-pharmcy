import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- إعدادات النظام ---
st.set_page_config(page_title="نظام غسق OS", layout="wide")

# --- تهيئة قواعد البيانات ---
def init_db():
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    # جدول المبيعات
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, dept TEXT, item TEXT, qty REAL, price REAL)''')
    # جدول المخزون
    c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, price REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- دالة إضافة صنف للمخزون ---
def add_to_inventory(name, qty, price):
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
    except sqlite3.IntegrityError: # إذا كان الصنف موجوداً، نحدث الكمية
        c.execute("UPDATE inventory SET quantity = quantity + ?, price = ? WHERE item_name = ?", (qty, price, name))
    conn.commit()
    conn.close()

# --- دالة إتمام البيع مع خصم المخزون ---
def process_sale(dept, item, qty):
    conn = sqlite3.connect('ghasaq_os.db')
    c = conn.cursor()
    # التحقق من وجود الصنف والكمية
    c.execute("SELECT quantity, price FROM inventory WHERE item_name = ?", (item,))
    result = c.fetchone()
    
    if result and result[0] >= qty:
        new_qty = result[0] - qty
        price = result[1]
        # خصم من المخزون
        c.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_qty, item))
        # تسجيل البيع
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO sales (timestamp, dept, item, qty, price) VALUES (?, ?, ?, ?, ?)",
                  (time, dept, item, qty, price))
        conn.commit()
        conn.close()
        return True, "تم البيع بنجاح!"
    else:
        conn.close()
        return False, "عذراً: الصنف غير موجود أو الكمية غير كافية."

# --- واجهة المستخدم ---
st.sidebar.title("🛠️ لوحة تحكم غسق")
page = st.sidebar.radio("الخدمات", ["📊 المبيعات اليومية", "🛒 نقطة البيع (POS)", "📦 إدارة المخزون"])

if page == "📊 المبيعات اليومية":
    st.title("📊 حركة المبيعات")
    conn = sqlite3.connect('ghasaq_os.db')
    df = pd.read_sql_query("SELECT * FROM sales ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

elif page == "🛒 نقطة البيع (POS)":
    st.title("🛒 نقطة البيع")
    item = st.text_input("اسم الصنف (كما هو في المخزن)")
    qty = st.number_input("الكمية", 1)
    if st.button("إتمام البيع"):
        success, msg = process_sale("صيدلية", item, qty)
        if success: st.success(msg)
        else: st.error(msg)

elif page == "📦 إدارة المخزون":
    st.title("📦 إضافة/تعديل المخزون")
    with st.form("inventory_form"):
        name = st.text_input("اسم الصنف")
        qty = st.number_input("الكمية المضافة")
        price = st.number_input("سعر الوحدة")
        if st.form_submit_button("حفظ في المخزن"):
            add_to_inventory(name, qty, price)
            st.success("تم تحديث المخزون!")
    
    st.subheader("المخزون الحالي")
    conn = sqlite3.connect('ghasaq_os.db')
    stock_df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    st.dataframe(stock_df)
