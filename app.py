import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from reportlab.pdfgen import canvas

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

# تهيئة الملفات
def init_files():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

init_files()

# واجهة النظام
st.title("💊 نظام غسق الطبي - النسخة الذهبية")
tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة الإدارة", "🛒 نقطة البيع", "📦 المخزون", "📜 سجل العمليات"])

# 1. لوحة الإدارة (تحليل البيانات)
with tab1:
    st.subheader("لوحة الأداء المالي")
    sales_df = pd.read_csv(SALES_FILE)
    if not sales_df.empty:
        sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
        fig = px.bar(sales_df, x='التاريخ', y='الإجمالي', title="الأرباح اليومية")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد مبيعات بعد.")

# 2. نقطة البيع (POS)
with tab2:
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        selected = st.selectbox("اختر الصنف للبيع:", df['الصنف'].unique())
        qty = st.number_input("الكمية", 1)
        if st.button("إتمام البيع"):
            price = df[df['الصنف'] == selected].iloc[-1]['السعر']
            total = qty * price
            # تسجيل العملية
            new_sale = pd.DataFrame([{'التاريخ': datetime.now(), 'الصنف': selected, 'الكمية': qty, 'الإجمالي': total}])
            new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
            st.success(f"تمت العملية! الإجمالي: {total}")
            st.balloons()
    else:
        st.warning("يرجى إضافة أصناف في تبويب المخزون أولاً.")

# 3. المخزون
with tab3:
    with st.form("add_item", clear_on_submit=True):
        name = st.text_input("اسم الصنف")
        barcode = st.text_input("الباركود")
        price = st.number_input("السعر")
        qty = st.number_input("الكمية")
        if st.form_submit_button("إضافة للمخزون"):
            new_item = pd.DataFrame([{'الباركود': barcode, 'الصنف': name, 'نوع_الوحدة': 'حبة', 'السعر': price, 'الكمية': qty}])
            new_item.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.rerun()
    st.dataframe(pd.read_csv(DB_FILE))

# 4. سجل العمليات
with tab4:
    st.dataframe(pd.read_csv(SALES_FILE))
