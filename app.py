import streamlit as st
import pandas as pd
import datetime
import os

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق - Ghasaq OS", layout="wide")

# --- تهيئة النظام ---
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = pd.DataFrame(columns=['التاريخ', 'القسم', 'الصنف/الخدمة', 'الكمية', 'السعر'])

# --- تصميم الفاتورة (مُنسق للطباعة) ---
def render_invoice(item, qty, price, department):
    return f"""
    <div style="border: 2px solid #333; padding: 20px; width: 300px; font-family: Arial;">
        <h2 style="text-align: center;">صيدلية ومعمل غسق</h2>
        <p>التاريخ: {datetime.date.today()}</p>
        <hr>
        <p>القسم: {department}</p>
        <p>الصنف: {item}</p>
        <p>الكمية: {qty}</p>
        <hr>
        <h3 style="text-align: center;">الإجمالي: {qty * price} ريال</h3>
    </div>
    """

# --- القائمة الجانبية ---
st.sidebar.title("🛠️ لوحة التحكم")
page = st.sidebar.radio("الخدمات", ["الرئيسية", "نقطة البيع (POS)", "إدارة المخزون/الخدمات"])

# --- الصفحة الرئيسية (المبيعات) ---
if page == "الرئيسية":
    st.title("📊 المبيعات اليومية")
    st.info("نظرة عامة على المبيعات (لا تشمل التكاليف/الأرباح)")
    # عرض جدول المبيعات فقط
    st.dataframe(st.session_state.sales_history[['التاريخ', 'القسم', 'الصنف/الخدمة', 'الكمية']], use_container_width=True)

# --- نقطة البيع (العمليات اليومية) ---
elif page == "نقطة البيع (POS)":
    st.title("🛒 نقطة البيع")
    tab1, tab2 = st.tabs(["💊 الصيدلية", "🧪 المعمل"])

    with tab1:
        with st.form("pharmacy_form"):
            item = st.text_input("اسم الدواء / الباركود")
            qty = st.number_input("الكمية", 1)
            price = st.number_input("السعر")
            if st.form_submit_button("إصدار الفاتورة"):
                st.session_state.invoice_data = {"item": item, "qty": qty, "price": price, "dept": "صيدلية"}
                st.success("تم تسجيل العملية")

    with tab2:
        with st.form("lab_form"):
            test = st.text_input("اسم الفحص/الخدمة")
            price_lab = st.number_input("السعر")
            if st.form_submit_button("تسجيل فحص"):
                st.session_state.invoice_data = {"item": test, "qty": 1, "price": price_lab, "dept": "معمل"}
                st.success("تم تسجيل الفحص")

    # عرض الفاتورة بعد التسجيل
    if 'invoice_data' in st.session_state:
        data = st.session_state.invoice_data
        st.markdown(render_invoice(data['item'], data['qty'], data['price'], data['dept']), unsafe_allow_html=True)
        st.button("إخفاء الفاتورة", on_click=lambda: st.session_state.pop('invoice_data'))

# --- إدارة المخزون ---
elif page == "إدارة المخزون/الخدمات":
    st.title("📦 قاعدة بيانات الأصناف")
    # هنا تضع كود إضافة أصناف جديدة للمخزون أو تحديث الأسعار
    st.warning("هذه المنطقة للمدير فقط")
