import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from reportlab.pdfgen import canvas
import os

st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

# تهيئة الملفات
if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

st.title("💊 نظام غسق الطبي - الواجهة المتكاملة")

# 1. قسم نقطة البيع (في الأعلى)
st.subheader("🛒 نقطة البيع السريع")
with st.form("pos_form"):
    df = pd.read_csv(DB_FILE)
    barcode = st.text_input("امسح الباركود أو اكتب اسم الصنف:")
    qty = st.number_input("الكمية", min_value=1, value=1)
    if st.form_submit_button("بيع وإصدار فاتورة"):
        item = df[(df['الباركود'].astype(str) == barcode) | (df['الصنف'] == barcode)]
        if not item.empty:
            total = qty * item.iloc[0]['السعر']
            # حفظ العملية
            new_sale = pd.DataFrame([{'التاريخ': datetime.now(), 'الصنف': item.iloc[0]['الصنف'], 'الكمية': qty, 'الإجمالي': total}])
            new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
            st.success(f"تمت العملية! الإجمالي: {total} ريال")
        else:
            st.error("صنف غير موجود.")

# 2. قسم التقارير والرسوم البيانية
st.subheader("📊 تقارير الأداء")
sales_df = pd.read_csv(SALES_FILE)
if not sales_df.empty:
    sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
    fig = px.bar(sales_df.groupby(sales_df['التاريخ'].dt.date)['الإجمالي'].sum().reset_index(), x='التاريخ', y='الإجمالي')
    st.plotly_chart(fig, use_container_width=True)

# 3. قسم المخزون
st.subheader("📦 المخزون الحالي")
st.dataframe(pd.read_csv(DB_FILE), use_container_width=True)

# 4. قسم سجل العمليات
st.subheader("📜 سجل المبيعات")
st.dataframe(pd.read_csv(SALES_FILE), use_container_width=True)
