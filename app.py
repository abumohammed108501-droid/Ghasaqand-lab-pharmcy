import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from reportlab.pdfgen import canvas

# إعداد الواجهة
st.set_page_config(page_title="نظام غسق Pro", layout="wide")

# -- إعدادات CSS للتصميم الاحترافي --
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# تهيئة الملفات
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['الباركود', 'الصنف', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)
if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

# القائمة الجانبية (Navigation)
st.sidebar.title("💊 نظام غسق Pro")
page = st.sidebar.radio("القائمة", ["📊 لوحة التحكم", "🛒 نقطة البيع", "📦 المخزون"])

# --- 1. لوحة التحكم ---
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

# --- 2. نقطة البيع (POS) ---
elif page == "🛒 نقطة البيع":
    st.title("🛒 نقطة البيع السريع")
    df = pd.read_csv(DB_FILE)
    
    with st.form("pos_form"):
        barcode = st.text_input("باركود / اسم الصنف")
        qty = st.number_input("الكمية", 1)
        if st.form_submit_button("إتمام البيع"):
            item = df[(df['الباركود'].astype(str) == barcode) | (df['الصنف'] == barcode)]
            if not item.empty:
                total = qty * item.iloc[0]['السعر']
                # حفظ المبيعات
                new_sale = pd.DataFrame([{'التاريخ': datetime.now(), 'الصنف': item.iloc[0]['الصنف'], 'الكمية': qty, 'الإجمالي': total}])
                new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
                st.success(f"تم البيع! الإجمالي: {total} ريال")
                # زر الفاتورة
                st.download_button("🖨️ طباعة فاتورة PDF", data="فاتورة صيدلية غسق", file_name="invoice.pdf")
            else:
                st.error("الصنف غير موجود.")

# --- 3. المخزون ---
elif page == "📦 المخزون":
    st.title("📦 إدارة المخزون")
    df = pd.read_csv(DB_FILE)
    st.dataframe(df, use_container_width=True)
    
    with st.expander("إضافة صنف جديد"):
        with st.form("add_item"):
            name = st.text_input("اسم الصنف")
            price = st.number_input("السعر")
            stock = st.number_input("الكمية")
            if st.form_submit_button("إضافة"):
                new_item = pd.DataFrame([{'الباركود': '000', 'الصنف': name, 'السعر': price, 'الكمية': stock}])
                new_item.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.rerun()
