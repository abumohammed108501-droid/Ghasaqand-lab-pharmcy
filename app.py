import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

DB_FILE = 'ghasaq_data.csv'

# التأكد من وجود ملف البيانات
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)

def load_data():
    return pd.read_csv(DB_FILE)

st.title("💊 نظام غسق الطبي - النسخة الذهبية")

# 1. إدارة المخزون
with st.expander("📦 إضافة صنف للمخزون"):
    with st.form("add_item_form"):
        name = st.text_input("اسم الصنف")
        barcode = st.text_input("الباركود")
        unit_type = st.radio("نوع الوحدة:", ["حبة", "كرتون"])
        price = st.number_input("السعر", min_value=0.0)
        qty = st.number_input("الكمية", min_value=0)
        submitted = st.form_submit_button("حفظ الصنف")
        if submitted:
            new_data = pd.DataFrame([{'الباركود': barcode, 'الصنف': name, 'نوع_الوحدة': unit_type, 'السعر': price, 'الكمية': qty}])
            new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success("تم حفظ الصنف!")
            st.rerun()

# 2. نقطة البيع
st.subheader("🛒 نقطة البيع (POS)")
df = load_data()

if not df.empty:
    selected_item = st.selectbox("اختر الصنف من المخزون:", df['الصنف'].unique())
    item_data = df[df['الصنف'] == selected_item]
    
    if not item_data.empty:
        item = item_data.iloc[0]
        st.write(f"الوحدة: {item['نوع_الوحدة']} | السعر: {item['السعر']}")
        
        sale_qty = st.number_input("الكمية المطلوبة", 1)
        if st.button("إتمام البيع"):
            total = sale_qty * item['السعر']
            st.success(f"إجمالي العملية: {total}")
    else:
        st.warning("الصنف غير موجود.")
else:
    st.info("المخزون فارغ، يرجى إضافة أصناف أولاً.")
