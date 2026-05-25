import streamlit as st
import pandas as pd
from streamlit_webrtc import webrtc_streamer # مكتبة الكاميرا
import av

st.set_page_config(layout="wide")
st.title("💊 نظام غسق - الطباعة والباركود المباشر")

# قارئ الباركود عبر الكاميرا
st.subheader("📷 قارئ الباركود المباشر")
webrtc_streamer(key="barcode-scanner") 

# نظام الطباعة (يفتح نافذة الطابعة في المتصفح)
def print_invoice(total):
    st.markdown(f"""
        <script>
            var printWindow = window.open('', '', 'height=400,width=600');
            printWindow.document.write('<html><body><h1>صيدلية غسق</h1><p>الإجمالي: {total} ريال</p></body></html>');
            printWindow.print();
            printWindow.close();
        </script>
    """, unsafe_allow_html=True)

# زر البيع مع أمر الطباعة
if st.button("إتمام البيع والطباعة"):
    print_invoice(500) # مثال تجريبي
    st.success("تم إرسال الفاتورة للطابعة!")
