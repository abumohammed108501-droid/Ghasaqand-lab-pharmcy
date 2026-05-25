import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")
st.title("💊 نظام غسق الطبي - الواجهة المتكاملة")

# تهيئة الملفات
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'
if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

# نموذج البيع (مع زر الطباعة)
with st.form("pos_form", clear_on_submit=True):
    barcode = st.text_input("مسح الباركود أو اسم الصنف")
    qty = st.number_input("الكمية", 1)
    submitted = st.form_submit_button("إتمام البيع والطباعة")
    
    if submitted:
        # هنا سيتم تسجيل البيع (هذا الجزء سيعمل بمجرد وجود بيانات في المخزون)
        st.success(f"تم البيع بنجاح! صنف: {barcode}")
        # زر لتحميل الفاتورة للطباعة
        st.download_button("🖨️ طباعة الفاتورة (PDF)", data="بيانات الفاتورة...", file_name="invoice.pdf")
