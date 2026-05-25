import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from reportlab.pdfgen import canvas
import os

st.set_page_config(page_title="نظام غسق الطبي - الاحترافي", layout="wide")

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

# 2. لوحة التقارير (اليومي، الشهري، السنوي)
with st.expander("📊 التقارير المالية"):
    sales_df = pd.read_csv(SALES_FILE)
    sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
    
    period = st.selectbox("اختر الفترة:", ["اليومية", "الشهرية", "السنوية"])
    if period == "اليومية":
        data = sales_df.groupby(sales_df['التاريخ'].dt.date)['الإجمالي'].sum()
    elif period == "الشهرية":
        data = sales_df.groupby(sales_df['التاريخ'].dt.to_period('M'))['الإجمالي'].sum()
    else:
        data = sales_df.groupby(sales_df['التاريخ'].dt.to_period('Y'))['الإجمالي'].sum()
    
    st.bar_chart(data)

# 3. نقطة البيع (مع دعم الباركود)
with st.form("pos_form"):
    df = pd.read_csv(DB_FILE)
    barcode_input = st.text_input("امسح الباركود أو اكتب اسم الصنف:")
    
    # البحث بالباركود أو الاسم
    item = df[(df['الباركود'] == barcode_input) | (df['الصنف'] == barcode_input)]
    
    if not item.empty:
        qty = st.number_input("الكمية", 1)
        if st.form_submit_button("بيع وإصدار فاتورة"):
            total = qty * item.iloc[0]['السعر']
            # حفظ العملية
            new_sale = pd.DataFrame([{'التاريخ': datetime.now(), 'الصنف': item.iloc[0]['الصنف'], 'الكمية': qty, 'الإجمالي': total}])
            new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
            
            # تحميل الفاتورة
            pdf = generate_invoice(item.iloc[0]['الصنف'], qty, total)
            with open(pdf, "rb") as f:
                st.download_button("📥 تحميل الفاتورة PDF", f, pdf)
    else:
        st.write("الرجاء إدخال باركود صحيح أو اسم الصنف.")
