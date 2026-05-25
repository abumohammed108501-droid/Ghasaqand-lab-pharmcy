import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام غسق الطبي - النسخة الذهبية", layout="wide")

# 2. ملف البيانات
DB_FILE = 'ghasaq_data.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)

# 3. وظيفة إنشاء PDF (الفاتورة)
def generate_pdf(item, qty, total):
    file_name = f"فاتورة_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.drawString(100, 750, f"نظام غسق الطبي - فاتورة بيع")
    c.drawString(100, 730, f"الصنف: {item}")
    c.drawString(100, 710, f"الكمية: {qty}")
    c.drawString(100, 690, f"الإجمالي: {total}")
    c.save()
    return file_name

# 4. الواجهة البرمجية
st.title("💊 نظام غسق الطبي - النسخة الذهبية")

# تبويب إدارة المخزون (الباركود + كرتون/حبة)
with st.expander("📦 إضافة صنف للمخزون (الباركود والوحدة)"):
    name = st.text_input("اسم الصنف")
    barcode = st.text_input("الباركود")
    unit_type = st.radio("نوع الوحدة:", ["حبة", "كرتون"])
    price = st.number_input("السعر")
    qty = st.number_input("الكمية")
    if st.button("حفظ الصنف"):
        new_item = {'الباركود': barcode, 'الصنف': name, 'نوع_الوحدة': unit_type, 'السعر': price, 'الكمية': qty}
        pd.DataFrame([new_item]).to_csv(DB_FILE, mode='a', header=False, index=False)
        st.success("تم حفظ الصنف مع الباركود والوحدة.")

# تبويب البيع (نقطة البيع)
st.subheader("🛒 نقطة البيع (POS)")
df = pd.read_csv(DB_FILE)
selected_item = st.selectbox("اختر الصنف من المخزون:", df['الصنف'].unique())
item_data = df[df['الصنف'] == selected_item].iloc[0]
st.write(f"الوحدة المتاحة: {item_data['نوع_الوحدة']} - السعر: {item_data['السعر']}")

sale_qty = st.number_input("الكمية المطلوبة", 1)
if st.button("إتمام البيع وطباعة PDF"):
    total = sale_qty * item_data['السعر']
    pdf_path = generate_pdf(selected_item, sale_qty, total)
    st.success(f"تم البيع! إجمالي: {total}")
    with open(pdf_path, "rb") as f:
        st.download_button("تحميل الفاتورة PDF", f, file_name=pdf_path)
