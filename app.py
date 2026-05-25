import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

DB_FILE = 'ghasaq_data.csv'

# وظيفة لإنشاء ملف نظيف تماماً
def reset_db():
    df = pd.DataFrame(columns=['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية'])
    df.to_csv(DB_FILE, index=False)
    st.warning("تمت إعادة ضبط قاعدة البيانات لتصحيح الأخطاء.")

# التأكد من صحة الأعمدة
if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE)
        expected_cols = ['الباركود', 'الصنف', 'نوع_الوحدة', 'السعر', 'الكمية']
        if not all(col in df.columns for col in expected_cols):
            reset_db()
    except:
        reset_db()
else:
    reset_db()

st.title("💊 نظام غسق الطبي - النسخة الذهبية")

# 1. إضافة صنف
with st.expander("📦 إضافة صنف للمخزون"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("اسم الصنف")
        barcode = st.text_input("الباركود")
        unit = st.radio("نوع الوحدة:", ["حبة", "كرتون"])
        price = st.number_input("السعر", min_value=0.0)
        qty = st.number_input("الكمية", min_value=0)
        if st.form_submit_button("حفظ"):
            new_row = pd.DataFrame([{'الباركود': barcode, 'الصنف': name, 'نوع_الوحدة': unit, 'السعر': price, 'الكمية': qty}])
            new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success("تم الحفظ!")
            st.rerun()

# 2. نقطة البيع
st.subheader("🛒 نقطة البيع (POS)")
df = pd.read_csv(DB_FILE)

if not df.empty:
    selected_name = st.selectbox("اختر الصنف:", df['الصنف'].unique())
    item_row = df[df['الصنف'] == selected_name].iloc[0]
    
    st.write(f"**نوع الوحدة:** {item_row['نوع_الوحدة']}")
    st.write(f"**السعر:** {item_row['السعر']}")
    
    sale_qty = st.number_input("الكمية المطلوبة", min_value=1)
    if st.button("إتمام البيع"):
        total = sale_qty * item_row['السعر']
        st.success(f"إجمالي العملية: {total}")
else:
    st.info("لا توجد أصناف في المخزون.")
