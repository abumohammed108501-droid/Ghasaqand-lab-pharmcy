import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide") # لضمان عرض النظام بشكل عرضي

st.title("💊 نظام غسق الطبي - لوحة تحكم احترافية")

# تهيئة البيانات
if not os.path.exists('ghasaq_data.csv'):
    pd.DataFrame(columns=['الباركود', 'الصنف', 'السعر', 'الكمية']).to_csv('ghasaq_data.csv', index=False)

# توزيع الواجهة إلى 3 أعمدة
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("🛒 نقطة البيع")
    with st.form("pos"):
        barcode = st.text_input("باركود / اسم الصنف")
        qty = st.number_input("الكمية", 1)
        if st.form_submit_button("بيع وإصدار فاتورة"):
            st.success("تم!")
            st.download_button("🖨️ طباعة الفاتورة", "فاتورة...")

with col2:
    st.subheader("📦 المخزون الحالي")
    df = pd.read_csv('ghasaq_data.csv')
    st.dataframe(df, use_container_width=True)

with col3:
    st.subheader("📈 الأداء المالي")
    # رسم بياني مصغر ليعطي شكل الـ Dashboard
    st.bar_chart({'مبيعات': [10, 20, 15, 30]})
    st.info("نظام التنبيهات: 2 أصناف ناقصة")
