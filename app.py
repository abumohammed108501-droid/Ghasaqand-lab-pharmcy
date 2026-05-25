import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

# تنسيق الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .metric-card {
        background-color: white; 
        padding: 20px; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-right: 5px solid #0EA5E9;
    }
    </style>
""", unsafe_allow_html=True)

# تهيئة قاعدة البيانات المؤقتة
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"الرمز": "1001", "الاسم": "بندول اكسترا", "الكمية": 50, "سعر البيع": 150},
        {"الرمز": "1002", "الاسم": "أموكسيسيلين", "الكمية": 30, "سعر البيع": 320}
    ])

st.title("🛒 شاشة البيع اليومي (POS)")

# عرض الأصناف
st.subheader("الأصناف المتاحة")
st.dataframe(st.session_state.inventory, use_container_width=True)

# عملية البيع
st.subheader("إضافة صنف للفاتورة")
selected_item = st.selectbox("اختر الصنف:", st.session_state.inventory['الاسم'].tolist())
qty = st.number_input("الكمية:", min_value=1, value=1)

if st.button("أضف للسلة"):
    st.success(f"تمت إضافة {qty} من {selected_item} إلى السلة")
