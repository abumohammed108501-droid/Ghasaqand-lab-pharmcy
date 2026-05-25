import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. إعدادات الصفحة والواجهة الطبية ---
st.set_page_config(page_title="نظام غسق الذهبي", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-right: 5px solid #0EA5E9; }
    h1 { color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات (CSV) ---
DB_FILE = 'ghasaq_data.csv'
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'السعر', 'الإجمالي']).to_csv(DB_FILE, index=False)

def load_data():
    return pd.read_csv(DB_FILE)

# --- 3. الواجهة التفاعلية ---
st.title("💊 نظام غسق الطبي - النسخة الذهبية")
tab1, tab2, tab3 = st.tabs(["🛒 نقطة البيع (POS)", "📦 إدارة المخزون", "📊 لوحة التحليل الذكي"])

# تبويب البيع
with tab1:
    st.subheader("إتمام عملية بيع جديدة")
    col1, col2 = st.columns(2)
    item = col1.text_input("اسم الصنف:")
    qty = col2.number_input("الكمية:", min_value=1)
    price = col1.number_input("سعر الوحدة:", min_value=0.0)
    
    if st.button("حفظ الفاتورة"):
        new_row = {'التاريخ': datetime.now().strftime("%Y-%m-%d"), 'الصنف': item, 'الكمية': qty, 'السعر': price, 'الإجمالي': qty * price}
        pd.DataFrame([new_row]).to_csv(DB_FILE, mode='a', header=False, index=False)
        st.success("تم تسجيل الفاتورة بنجاح!")

# تبويب المخزون
with tab2:
    st.subheader("الأصناف والمخزون")
    st.info("نظام تتبع المخزون اللحظي مفعل.")
    st.dataframe(load_data(), use_container_width=True)

# تبويب التحليل (النسخة الذهبية)
with tab3:
    st.subheader("تحليلات الأداء (السنوي والشهري)")
    df = load_data()
    if not df.empty:
        df['التاريخ'] = pd.to_datetime(df['التاريخ'])
        
        # تحليل أفضل الشهور
        df['الشهر'] = df['التاريخ'].dt.strftime('%Y-%m')
        monthly_sales = df.groupby('الشهر')['الإجمالي'].sum().reset_index()
        
        fig = px.bar(monthly_sales, x='الشهر', y='الإجمالي', title="إجمالي المبيعات حسب الشهر", color='الإجمالي', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
        
        # أفضل صنف
        top_item = df.groupby('الصنف')['الكمية'].sum().idxmax()
        st.metric("الأكثر مبيعاً", top_item)
    else:
        st.warning("لا توجد بيانات كافية للتحليل حالياً.")

# --- 4. تذييل النظام ---
st.sidebar.markdown("---")
st.sidebar.write("نظام غسق الطبي | النسخة الذهبية 2026")
