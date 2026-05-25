import streamlit as st
import pandas as pd
import os

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")
DB_FILE = 'ghasaq_data.csv'

# وظيفة التأكد من قاعدة البيانات
def check_db():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        # التأكد من الأعمدة
        if 'الصنف' not in df.columns:
            pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']).to_csv(DB_FILE, index=False)

check_db()

st.title("💊 نظام غسق الطبي - النسخة الذهبية")

# 1. إضافة صنف (إدارة المخزون)
with st.expander("📦 إضافة صنف للمخزون"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("اسم الصنف")
        barcode = st.text_input("الباركود")
        unit = st.radio("نوع الوحدة:", ["حبة", "كرتون"], horizontal=True)
        price = st.number_input("السعر", min_value=0.0)
        qty = st.number_input("الكمية", min_value=0)
        if st.form_submit_button("حفظ الصنف"):
            new_row = pd.DataFrame([{'الباركود': barcode, 'الصنف': name, 'نوع_الوحدة': unit, 'السعر': price, 'الكمية': qty}])
            new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success(f"تم إضافة {name} بنجاح!")
            st.rerun()

# 2. نقطة البيع (POS)
st.subheader("🛒 نقطة البيع (POS)")
df = pd.read_csv(DB_FILE)

if not df.empty:
    selected_name = st.selectbox("اختر الصنف:", df['الصنف'].unique())
    # اختيار الصنف الأخير المدخل إذا تكررت الأسماء
    item_row = df[df['الصنف'] == selected_name].iloc[-1]
    
    st.info(f"الوحدة: {item_row['نوع_الوحدة']} | السعر: {item_row['السعر']}")
    
    sale_qty = st.number_input("الكمية المطلوبة", min_value=1)
    if st.button("إتمام البيع"):
        total = sale_qty * float(item_row['السعر'])
        st.success(f"تمت العملية! الإجمالي: {total} ريال")
else:
    st.warning("المخزون فارغ. يرجى إضافة أصناف من الأعلى.")
