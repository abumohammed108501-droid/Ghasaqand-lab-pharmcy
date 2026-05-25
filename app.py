import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. إعداد الصفحة والستايل الاحترافي (CSS)
st.set_page_config(page_title="غسق - لوحة التحكم الإدارية", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* خلفية التطبيق الداكنة */
    .stApp {
        background-color: #0b1a27;
        color: white;
    }
    /* ستايل البطاقات (Cards) */
    .metric-card {
        background-color: #1b2b3b;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #2e3f4f;
        text-align: center;
        margin-bottom: 10px;
    }
    /* العناوين */
    h1, h2, h3 {
        color: #4ecdc4 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* إخفاء التبويبات التقليدية وجعلها مودرن */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1b2b3b;
        border-radius: 10px;
        color: white;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ملفات البيانات
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=['التاريخ', 'الصنف', 'الكمية', 'الإجمالي']).to_csv(SALES_FILE, index=False)

# --- واجهة Sidebar (مثل القائمة الجانبية في الصورة) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=100)
    st.title("Ghasaq Pro")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["🏠 لوحة التحكم", "🛒 نقطة البيع", "📦 إدارة المخزون", "⚙️ الإعدادات"])

# --- القسم الرئيسي: لوحة التحكم (Dashboard) ---
if menu == "🏠 لوحة التحكم":
    st.title("📊Hospital Analytics Dashboard")
    
    # صف البطاقات العلوية (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    sales_df = pd.read_csv(SALES_FILE)
    total_revenue = sales_df['الإجمالي'].sum() if not sales_df.empty else 0
    total_items = len(pd.read_csv(DB_FILE))
    
    with col1:
        st.markdown(f"<div class='metric-card'><h3>💰 الأرباح</h3><h2>{total_revenue}</h2><p>ريال سعودي</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>📦 الأصناف</h3><h2>{total_items}</h2><p>صنف مسجل</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>📈 المبيعات</h3><h2>{len(sales_df)}</h2><p>عملية اليوم</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h3>🔔 تنبيهات</h3><h2 style='color:ff6b6b'>2</h2><p>نقص مخزون</p></div>", unsafe_allow_html=True)

    # الرسوم البيانية (مثل الصورة)
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📈 Inpatient Trends (المبيعات الزمنية)")
        if not sales_df.empty:
            sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
            fig = px.line(sales_df, x='التاريخ', y='الإجمالي', template="plotly_dark", color_discrete_sequence=['#4ecdc4'])
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.subheader("💊 Stock Level (حالة المخزون)")
        stock_data = {"الأدوية": [70, 30, 50], "الحالة": ["Paracetamol", "Amoxicillin", "Panadol"]}
        fig2 = px.bar(stock_data, x="الحالة", y="الأدوية", template="plotly_dark", color="الحالة")
        st.plotly_chart(fig2, use_container_width=True)

# --- قسم نقطة البيع (POS) ---
elif menu == "🛒 نقطة البيع":
    st.title("🛒 Quick POS Terminal")
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            barcode = st.text_input("🔍 امسح الباركود أو اكتب الاسم")
        with col_b:
            qty = st.number_input("الكمية", min_value=1)
        
        if st.button("إتمام العملية وإصدار الفاتورة"):
            st.success("✅ تم تسجيل العملية بنجاح!")
            st.balloons()

# --- قسم المخزون ---
elif menu == "📦 إدارة المخزون":
    st.title("📦 Inventory Management")
    df = pd.read_csv(DB_FILE)
    st.dataframe(df.style.set_properties(**{'background-color': '#1b2b3b', 'color': 'white'}))
