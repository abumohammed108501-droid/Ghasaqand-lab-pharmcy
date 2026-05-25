import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

# تنسيق الواجهة (CSS)
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

# تهيئة قاعدة البيانات في الذاكرة (Inventory)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"الرمز": "1001", "الاسم": "بندول اكسترا", "الكمية": 50, "سعر البيع": 150},
        {"الرمز": "1002", "الاسم": "أموكسيسيلين", "الكمية": 30, "سعر البيع": 320}
    ])

# العنوان الرئيسي
st.title("💊 نظام غسق الطبي")

# شاشة البيع اليومي
st.subheader("🛒 شاشة البيع اليومي (POS)")
st.dataframe(st.session_state.inventory, use_container_width=True)

selected_item = st.selectbox("اختر الصنف للبيع:", st.session_state.inventory['الاسم'].tolist())
qty = st.number_input("الكمية:", min_value=1, value=1)

if st.button("أضف للسلة"):
    st.success(f"تم إعداد فاتورة لـ {qty} من {selected_item}")

st.markdown("---")

# إدارة المخزون
st.subheader("📦 إدارة المخزون")
with st.form("add_item_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("اسم الصنف الجديد:")
        new_price = st.number_input("سعر البيع:", min_value=0)
    with col2:
        new_qty = st.number_input("الكمية:", min_value=0)
        new_code = st.text_input("الرمز (الباركود):")
    
    submitted = st.form_submit_button("إضافة صنف للمخزون")
    if submitted:
        new_item = {"الرمز": new_code, "الاسم": new_name, "الكمية": new_qty, "سعر البيع": new_price}
        st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_item])], ignore_index=True)
        st.success(f"تم إضافة {new_name} للمخزون بنجاح!")
        st.rerun()
