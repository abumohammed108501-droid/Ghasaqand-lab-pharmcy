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

st.title("💊 نظام غسق الطبي - لوحة الإدارة المتكاملة")

# 1. نظام الفواتير PDF
def generate_invoice(item, qty, total):
    file_name = f"invoice_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    c = canvas.Canvas(file_name)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "صيدلية غسق - فاتورة بيع")
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(100, 730, f"الصنف: {item}")
    c.drawString(100, 710, f"الكمية: {qty}")
    c.drawString(100, 690, f"الإجمالي: {total} ريال")
    c.save()
    return file_name

# 2. لوحة التقارير
with st.expander("📊 التقارير المالية"):
    if os.path.exists(SALES_FILE):
        sales_df = pd.read_csv(SALES_FILE)
        sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
        
        period = st.selectbox("اختر الفترة:", ["اليومية", "الشهرية", "السنوية"])
        if period == "اليومية":
            data = sales_df.groupby(sales_df['التاريخ'].dt.date)['الإجمالي'].sum()
        elif period == "الشهرية":
            data = sales_df.groupby(sales_df['التاريخ'].dt.to_period('M').astype(str))['الإجمالي'].sum()
        else:
            data = sales_df.groupby(sales_df['التاريخ'].dt.to_period('Y').astype(str))['الإجمالي'].sum()
        
        st.bar_chart(data)

# 3. نقطة البيع (تم إصلاح خطأ الزر هنا)
with st.form("pos_form"):
    df = pd.read_csv(DB_FILE)
    barcode_input = st.text_input("امسح الباركود أو اكتب اسم الصنف:")
    qty = st.number_input("الكمية", min_value=1, value=1)
    
    # زر الإرسال داخل النموذج (حل المشكلة)
    submitted = st.form_submit_button("بيع وإصدار فاتورة")
    
    if submitted:
        item = df[(df['الباركود'].astype(str) == barcode_input) | (df['الصنف'] == barcode_input)]
        if not item.empty:
            total = qty * item.iloc[0]['السعر']
            new_sale = pd.DataFrame([{'التاريخ': datetime.now(), 'الصنف': item.iloc[0]['الصنف'], 'الكمية': qty, 'الإجمالي': total}])
            new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
            
            pdf = generate_invoice(item.iloc[0]['الصنف'], qty, total)
            with open(pdf, "rb") as f:
                st.download_button("📥 تحميل الفاتورة PDF", f, pdf)
            st.success("تمت العملية بنجاح!")
        else:
            st.error("الصنف غير موجود في المخزون.")
