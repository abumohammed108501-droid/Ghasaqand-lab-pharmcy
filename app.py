import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام Ghassaq ERP الاحترافي", layout="wide", initial_sidebar_state="expanded")

# --- الاتصال بقاعدة البيانات ---
conn = sqlite3.connect("erp_database.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    barcode TEXT PRIMARY KEY, name TEXT, quantity INTEGER, 
                    min_limit INTEGER, expiry_date TEXT, price REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT, name TEXT, 
                    quantity INTEGER, total_price REAL, date TEXT, customer_phone TEXT)''')
conn.commit()

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("📊 نظام إدارة العمليات")
page = st.sidebar.radio("انتقل إلى:", ["🛒 شاشة البيع اليومي", "📦 إدارة المخزون والإنذارات", "📈 لوحة التحكم والتقارير"])

# ==========================================
# 1. شاشة البيع اليومي (POS)
# ==========================================
if page == "🛒 شاشة البيع اليومي":
    st.title("🛒 نقطة البيع السريعة (POS)")
    
    # جلب المنتجات المتاحة
    df_inv = pd.read_sql_query("SELECT * FROM inventory", conn)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("الفاتورة الحالية")
        barcode_input = st.text_input("🔍 امسح الباركود أو أدخل الرمز هنا:")
        
        product = df_inv[df_inv['barcode'] == barcode_input]
        
        if not product.empty:
            p_name = product.iloc[0]['name']
            p_price = product.iloc[0]['price']
            p_stock = product.iloc[0]['quantity']
            
            st.success(f"المنتج: {p_name} | السعر: {p_price} SDG | المتاح: {p_stock}")
            
            qty = st.number_input("الكمية المطلوبة:", min_value=1, max_value=int(p_stock) if p_stock > 0 else 1, value=1)
            phone = st.text_input("رقم هاتف العميل (لإرسال الفاتورة عبر الواتساب):", placeholder="مثال: 2499xxxxxxx")
            
            total = qty * p_price
            st.markdown(f"### 💰 الإجمالي: **{total} SDG**")
            
            if st.button("✅ إتمام البيع وطباعة الفاتورة"):
                if p_stock >= qty:
                    # تحديث المخزون
                    new_qty = p_stock - qty
                    cursor.execute("UPDATE inventory SET quantity = ? WHERE barcode = ?", (new_qty, barcode_input))
                    # تسجيل المبيعات
                    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO sales (barcode, name, quantity, total_price, date, customer_phone) VALUES (?, ?, ?, ?, ?, ?)",
                                   (barcode_input, p_name, qty, total, sale_date, phone))
                    conn.commit()
                    st.balloons()
                    st.success("تم تسجيل العملية بنجاح وتحديث المخزون!")
                    
                    # رابط الواتساب الجاهز لإرسال التقارير للعميل مجاناً
                    if phone:
                        msg = f"شكرًا لتعاملك معنا. فاتورتك لمنتج {p_name}، الكمية: {qty}، الإجمالي: {total} SDG. نتمنى لكم يوماً سعيداً!"
                        msg_encoded = urllib.parse.quote(msg)
                        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={msg_encoded}"
                        st.markdown(f"[📱 اضغط هنا لإرسال الفاتورة فوراً للعميل عبر الواتساب]({whatsapp_url})")
                else:
                    st.error("الكمية في المخزون غير كافية!")

# ==========================================
# 2. إدارة المخزون والإنذارات
# ==========================================
elif page == "📦 إدارة المخزون والإنذارات":
    st.title("📦 إدارة المخزون والمنتجات")
    
    # إضافة منتج جديد
    with st.expander("➕ إضافة منتج جديد للمخزون"):
        with st.form("add_product"):
            b_code = st.text_input("الباركود:")
            name = st.text_input("اسم المنتج:")
            qty = st.number_input("الكمية الابتدائية:", min_value=0, value=10)
            min_l = st.number_input("حد الأمان (الإنذار للكمية):", min_value=1, value=5)
            exp = st.date_input("تاريخ انتهاء الصلاحية:")
            price = st.number_input("سعر البيع:", min_value=0.0, value=100.0)
            
            if st.form_submit_button("حفظ المنتج"):
                try:
                    cursor.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)", (b_code, name, qty, min_l, str(exp), price))
                    conn.commit()
                    st.success("تم إضافة المنتج بنجاح!")
                except:
                    st.error("الباركود مسجل مسبقاً لمنتج آخر!")

    # عرض البيانات والإنذارات
    df_inv = pd.read_sql_query("SELECT * FROM inventory", conn)
    st.subheader("📊 جرد المخزون الحالي")
    st.dataframe(df_inv)
    
    # قسم الإنذارات الذكية
    st.subheader("🚨 نظام التنبيهات والإنذارات المبكرة")
    today = datetime.now().date()
    danger_zone = today + timedelta(days=60) # إنذار قبل شهرين من انتهاء الصلاحية
    
    for idx, row in df_inv.iterrows():
        # إنذار الكمية
        if row['quantity'] <= row['min_limit']:
            st.warning(f"⚠️ تنبيه كمية: المنتج **[{row['name']}]** شارف على النفاد! المتبقي: {row['quantity']} فقط.")
        
        # إنذار الصلاحية
        try:
            exp_date = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
            if exp_date <= today:
                st.error(f"❌ انتهت الصلاحية: المنتج **[{row['name']}]** منتهي الصلاحية بتاريخ ({row['expiry_date']})! يرجى إعدامه.")
            elif exp_date <= danger_zone:
                st.info(f"⏳ قرب انتهاء الصلاحية: المنتج **[{row['name']}]** سينتهي قريباً بتاريخ ({row['expiry_date']}).")
        except:
            pass

# ==========================================
# 3. لوحة التحكم والتقارير البيانية
# ==========================================
elif page == "📈 لوحة التحكم والتقارير":
    st.title("📈 التحليلات الإحصائية وذكاء الأعمال")
    
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    
    if df_sales.empty:
        st.info("لا توجد مبيعات مسجلة حتى الآن لعرض التقارير والرسوم البيانية.")
    else:
        # تحويل التاريخ لمعالجة البيانات زمنيًا
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        df_sales['Month'] = df_sales['date'].dt.strftime('%B')
        df_sales['Year'] = df_sales['date'].dt.strftime('%Y')
        
        # إجمالي الأرقام الكبيرة
        total_revenue = df_sales['total_price'].sum()
        st.metric(label="💰 إجمالي حجم المبيعات الكلي", value=f"{total_revenue:,.2f} SDG")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🍩 نسبة مبيعات المنتجات (Pie Chart)")
            fig_pie = px.pie(df_sales, values='total_price', names='name', hole=0.4, title="توزيع المبيعات حسب الصنف")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            st.subheader("📊 أداء المبيعات الشهرية")
            fig_bar = px.bar(df_sales, x='Month', y='total_price', color='Year', barmode='group', title="المبيعات حسب الأشهر والسنوات")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # تحديد أفضل شهر وأفضل سنة تلقائياً
        st.subheader("🏆 مؤشرات الأداء والقمم البيعية")
        
        best_month = df_sales.groupby('Month')['total_price'].sum().idxmax()
        best_month_val = df_sales.groupby('Month')['total_price'].sum().max()
        
        best_year = df_sales.groupby('Year')['total_price'].sum().idxmax()
        best_year_val = df_sales.groupby('Year')['total_price'].sum().max()
        
        c1, c2 = st.columns(2)
        c1.success(f"🌟 **أفضل شهر مبيعات:** {best_month} (بإجمالي أرباح: {best_month_val:,.2f} SDG)")
        c2.success(f"👑 **أفضل سنة مبيعات:** {best_year} (بإجمالي أرباح: {best_year_val:,.2f} SDG)")
