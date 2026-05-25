import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

# التأكد من وجود ملفات البيانات
if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

st.title("💊 نظام غسق الطبي - النسخة الذهبية")

# التبويبات
tab1, tab2, tab3 = st.tabs(["🛒 نقطة البيع", "📦 المخزون", "📜 سجل العمليات"])

# 1. نقطة البيع
with tab1:
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        selected_name = st.selectbox("اختر الصنف:", df['الصنف'].unique())
        item = df[df['الصنف'] == selected_name].iloc[-1]
        sale_qty = st.number_input("الكمية", min_value=1)
        
        if st.button("إتمام البيع"):
            total = sale_qty * float(item['السعر'])
            # حفظ في سجل العمليات
            new_sale = pd.DataFrame([{'التاريخ': datetime.now().strftime("%Y-%m-%d %H:%M"), 'الصنف': selected_name, 'الكمية': sale_qty, 'الإجمالي': total}])
            new_sale.to_csv(SALES_FILE, mode='a', header=False, index=False)
            st.success(f"تم البيع! الإجمالي: {total} ريال")
    else:
        st.warning("المخزون فارغ!")

# 2. سجل العمليات
with tab3:
    st.subheader("📜 سجل مبيعات اليوم")
    sales_df = pd.read_csv(SALES_FILE)
    st.dataframe(sales_df, use_container_width=True)
