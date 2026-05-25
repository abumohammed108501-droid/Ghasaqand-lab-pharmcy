import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide") # هذا السطر هو الأهم لجعل الواجهة عريضة

st.title("💊 نظام غسق الطبي - لوحة التحكم العرضية")

DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

# صف أول يحتوي على أعمدة (نقطة البيع + المخزون)
col1, col2 = st.columns([1, 2]) 

with col1:
    st.subheader("🛒 نقطة البيع")
    # هنا نضع كود البيع المختصر
    barcode = st.text_input("باركود")
    if st.button("بيع"):
        st.success("تم!")

with col2:
    st.subheader("📦 جدول المخزون الحالي")
    if os.path.exists(DB_FILE):
        st.dataframe(pd.read_csv(DB_FILE), use_container_width=True)

# صف ثانٍ للتقارير (عرضي بالكامل)
st.markdown("---")
st.subheader("📈 تقارير الأداء")
if os.path.exists(SALES_FILE):
    sales_df = pd.read_csv(SALES_FILE)
    if not sales_df.empty:
        # رسم بياني عرضي يملأ الشاشة
        fig = px.bar(sales_df, x='التاريخ', y='الإجمالي', orientation='v')
        st.plotly_chart(fig, use_container_width=True)
