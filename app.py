import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("💊 نظام غسق الطبي")

# زر بيع مبسط جداً بدون تعقيد الكاميرا
with st.form("pos_form"):
    barcode = st.text_input("امسح الباركود أو اكتب اسم الصنف")
    qty = st.number_input("الكمية", 1)
    # هذا الزر سيظهر الآن ولن يختفي
    submitted = st.form_submit_button("إتمام البيع")
    
    if submitted:
        st.success(f"تم تسجيل بيع {qty} من الصنف {barcode}")
        # هنا سيظهر زر تحميل الفاتورة للطباعة
        st.download_button("📥 تحميل الفاتورة للطباعة", data="فاتورة صيدلية غسق...", file_name="invoice.txt")
