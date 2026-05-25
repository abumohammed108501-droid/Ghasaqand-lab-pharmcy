import streamlit as st
from reportlab.pdfgen import canvas
import os

st.set_page_config(layout="wide")
st.title("💊 نظام غسق الطبي - الإصدار الاحترافي")

# -- 1. قسم الكاميرا (لتصوير المستندات أو الباركود) --
st.subheader("📷 الكاميرا (تصوير الوصفات أو الباركود)")
img_file = st.camera_input("التقاط صورة")

if img_file:
    st.success("تم التقاط الصورة بنجاح!")
    st.image(img_file)

# -- 2. قسم الفاتورة (PDF) --
st.subheader("🖨️ إصدار الفاتورة")
invoice_data = st.text_area("تفاصيل الفاتورة", "صيدلية غسق - دواء: بانادول - السعر: 10 ريال")

def create_pdf(text):
    pdf_path = "invoice.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "صيدلية غسق - فاتورة بيع")
    c.drawString(100, 730, text)
    c.save()
    return pdf_path

if st.button("إنشاء وتحميل الفاتورة PDF"):
    pdf_file = create_pdf(invoice_data)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 تحميل الفاتورة الآن", f, file_name="invoice.pdf")
