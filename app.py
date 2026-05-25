import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from reportlab.pdfgen import canvas

st.set_page_config(page_title="نظام غسق الإداري", layout="wide")
DB_FILE = 'ghasaq_data.csv'
SALES_FILE = 'sales_history.csv'

# 1. لوحة التحكم (الرسوم البيانية)
def show_dashboard():
    st.subheader("📊 لوحة الأداء المالي")
    sales_df = pd.read_csv(SALES_FILE)
    if not sales_df.empty:
        sales_df['التاريخ'] = pd.to_datetime(sales_df['التاريخ'])
        daily_sales = sales_df.groupby(sales_df['التاريخ'].dt.date)['الإجمالي'].sum().reset_index()
        fig = px.line(daily_sales, x='التاريخ', y='الإجمالي', title="الأرباح اليومية")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد مبيعات لعرض التقارير.")

# 2. نظام التنبيهات
def check_stock():
    df = pd.read_csv(DB_FILE)
    low_stock = df[df['الكمية'] < 5] # تنبيه إذا كانت الكمية أقل من 5
    if not low_stock.empty:
        st.sidebar.error("⚠️ تنبيه: أصناف قاربت على النفاذ!")
        st.sidebar.table(low_stock[['الصنف', 'الكمية']])

# 3. إنشاء فاتورة PDF
def create_pdf(item, qty, total):
    file_name = "invoice.pdf"
    c = canvas.Canvas(file_name)
    c.drawString(100, 800, f"صيدلية غسق - فاتورة مريض")
    c.drawString(100, 780, f"الصنف: {item}")
    c.drawString(100, 760, f"الكمية: {qty}")
    c.drawString(100, 740, f"الإجمالي: {total} ريال")
    c.save()
    return file_name

# --- واجهة النظام ---
st.title("💊 نظام غسق الطبي - لوحة الإدارة")
check_stock() # تشغيل نظام التنبيهات
tab1, tab2, tab3 = st.tabs(["📊 لوحة التحكم", "🛒 نقطة البيع", "📦 المخزون"])

with tab1:
    show_dashboard()

with tab2:
    # (كود البيع مع إضافة زر تحميل الفاتورة)
    df = pd.read_csv(DB_FILE)
    selected = st.selectbox("اختر الصنف:", df['الصنف'].unique())
    qty = st.number_input("الكمية", 1)
    if st.button("إتمام البيع"):
        # ... (كود حفظ البيع كما في السابق)
        pdf = create_pdf(selected, qty, 100) # مثال تجريبي
        with open(pdf, "rb") as f:
            st.download_button("📥 تحميل الفاتورة PDF", f, "invoice.pdf")

with tab3:
    st.dataframe(pd.read_csv(DB_FILE))
