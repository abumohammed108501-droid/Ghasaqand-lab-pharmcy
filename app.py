import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from reportlab.pdfgen import canvas
import io

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام غسق Pro", layout="wide")

# 2. تهيئة الملفات
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['الباركود', 'الصنف', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)
if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

# 3. القائمة الجانبية (للتنظيم)
st.sidebar.title("💊 نظام غسق Pro")
page = st.sidebar.radio("القائمة", ["📊 لوحة التحكم", "🛒 نقطة البيع", "📦 المخزون"])

# --- صفحة 1: لوحة التحكم ---
if page == "📊 لوحة التحكم":
    st.title("📊 لوحة الأداء المالي")
    sales_df = pd.read_csv(SALES_FILE)
    if not sales_df.empty:
        sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
        fig = px.bar(sales_df.groupby(sales_df['التاريخ'].dt.date)['الإجمالي'].sum().reset_index(), 
                     x='التاريخ', y='الإجمالي', title="الأرباح اليومية")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات مبيعات لعرضها.")

# --- صفحة 2: نقطة البيع ---
elif page == "🛒 نقطة البيع":
    st.title("🛒 نقطة البيع السريع")
    # الكاميرا
    img_file = st.camera_input("📷 تصوير الوصفة أو الباركود")
    
    with st.form("pos_form"):
        barcode = st.text_input("باركود / اسم الصنف")
        qty = st.number_input("الكمية", 1)
        
        if st.form_submit_button("إتمام البيع"):
            st.success(f"تم تسجيل البيع للصنف {barcode}!")
            # تحضير محتوى الفاتورة كـ Bytes (حل خطأ Download Button)
            invoice_text = f"فاتورة صيدلية غسق\nالصنف: {barcode}\nالكمية: {qty}\nالتاريخ: {datetime.now()}"
            st.download_button(
                label="🖨️ تحميل الفاتورة",
                data=invoice_text,
                file_name="invoice.txt",
                mime="text/plain"
            )

# --- صفحة 3: المخزون ---
elif page == "📦 المخزون":
    st.title("📦 إدارة المخزون")
    df = pd.read_csv(DB_FILE)
    st.dataframe(df, use_container_width=True)
    
    with st.expander("إضافة صنف جديد"):
        with st.form("add_item"):
            name = st.text_input("اسم الصنف")
            price = st.number_input("السعر")
            stock = st.number_input("الكمية")
            if st.form_submit_button("حفظ"):
                new_row = pd.DataFrame([{'الباركود': '000', 'الصنف': name, 'السعر': price, 'الكمية': stock}])
                new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.rerun()
