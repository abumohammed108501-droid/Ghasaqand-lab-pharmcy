import streamlit as st
import pandas as pd
import datetime

# 1. إعدادات النظام
st.set_page_config(page_title="نظام غسق OS", layout="wide")

# 2. تهيئة الذاكرة
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = pd.DataFrame(columns=['التاريخ', 'القسم', 'الصنف', 'الكمية'])
if 'invoice_data' not in st.session_state:
    st.session_state.invoice_data = None

# --- دالة عرض الفاتورة (للطباعة) ---
def show_printable_invoice(item, qty, price, dept):
    total = qty * price
    return f"""
    <div style="border: 2px solid #2c3e50; padding: 25px; width: 350px; background-color: #fff; border-radius: 10px; color: #000;">
        <h2 style="text-align: center; color: #2c3e50;">صيدلية ومعمل غسق</h2>
        <p style="text-align: center;">{datetime.date.today()}</p>
        <hr>
        <p><strong>القسم:</strong> {dept}</p>
        <p><strong>البيان:</strong> {item}</p>
        <p><strong>الكمية:</strong> {qty}</p>
        <hr>
        <h3 style="text-align: center;">الإجمالي: {total} ريال</h3>
    </div>
    """

# --- القائمة الجانبية ---
st.sidebar.title("🛠️ لوحة تحكم غسق")
page = st.sidebar.radio("الخدمات", ["📊 المبيعات اليومية", "🛒 نقطة البيع (POS)", "📦 إدارة المخزون"])

# --- الصفحة 1: المبيعات ---
if page == "📊 المبيعات اليومية":
    st.title("📊 حركة المبيعات اليومية")
    
    if not st.session_state.sales_history.empty:
        st.dataframe(st.session_state.sales_history, use_container_width=True)
        
        # إضافة زر التحميل هنا (دمجناه في مكانه الصحيح)
        csv = st.session_state.sales_history.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل تقرير المبيعات (CSV)",
            data=csv,
            file_name=f"sales_report_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("لا توجد عمليات مسجلة اليوم.")

# --- الصفحة 2: نقطة البيع ---
elif page == "🛒 نقطة البيع (POS)":
    st.title("🛒 نقطة البيع الموحدة")
    
    tab1, tab2 = st.tabs(["💊 الصيدلية", "🧪 المعمل"])

    with tab1:
        with st.form("pharmacy_form", clear_on_submit=True):
            item = st.text_input("اسم الدواء / الباركود")
            qty = st.number_input("الكمية", 1)
            price = st.number_input("السعر")
            if st.form_submit_button("إتمام البيع"):
                new_sale = {'التاريخ': datetime.datetime.now().strftime("%H:%M"), 'القسم': 'صيدلية', 'الصنف': item, 'الكمية': qty}
                st.session_state.sales_history = pd.concat([st.session_state.sales_history, pd.DataFrame([new_sale])], ignore_index=True)
                st.session_state.invoice_data = {"item": item, "qty": qty, "price": price, "dept": "صيدلية"}
                st.rerun()

    with tab2:
        with st.form("lab_form", clear_on_submit=True):
            test_name = st.text_input("اسم الفحص/الخدمة")
            price_lab = st.number_input("السعر")
            if st.form_submit_button("تسجيل الفحص"):
                new_sale = {'التاريخ': datetime.datetime.now().strftime("%H:%M"), 'القسم': 'معمل', 'الصنف': test_name, 'الكمية': 1}
                st.session_state.sales_history = pd.concat([st.session_state.sales_history, pd.DataFrame([new_sale])], ignore_index=True)
                st.session_state.invoice_data = {"item": test_name, "qty": 1, "price": price_lab, "dept": "معمل"}
                st.rerun()

    if st.session_state.invoice_data:
        data = st.session_state.invoice_data
        st.markdown(show_printable_invoice(data['item'], data['qty'], data['price'], data['dept']), unsafe_allow_html=True)
        if st.button("إغلاق الفاتورة"):
            st.session_state.invoice_data = None
            st.rerun()
