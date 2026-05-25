import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import requests
import os

# مكتبات توليد الـ PDF والتنسيق
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# مكتبات معالجة اللغة العربية من اليمين إلى اليسار
import arabic_reshaper
from bidi.algorithm import get_display

from PIL import Image
import datetime

# إعدادات الصفحة الأساسية لنظام غسق
st.set_page_config(page_title="نظام غسق لإدارة العمليات", page_icon="💊", layout="wide")

# دالة ذكية لتحميل خط عربي وتثبيته في السيرفر مؤقتاً
@st.cache_resource
def setup_arabic_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            response = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            return False
    try:
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
        return True
    except:
        return False

font_status = setup_arabic_font()

# دالة لتجهيز النصوص العربية لـ PDF
def format_arabic(text):
    if not text:
        return ""
    # إعادة تشكيل الحروف وعكس الاتجاه لتبدأ من اليمين لليسار بشكل صحيح
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# تهيئة قاعدة البيانات المؤقتة في الذاكرة (مع إضافة الاسم الإنجليزي الرديف)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"الرمز": "1001", "الاسم العربي": "بندول اكسترا", "الاسم الإنجليزي": "Panadol Extra", "النوع": "دواء", "الكمية": 50, "سعر الشراء": 120, "سعر البيع": 150},
        {"الرمز": "1002", "الاسم العربي": "أموكسيسيلين 500 ملغ", "الاسم الإنجليزي": "Amoxicillin 500mg", "النوع": "دواء", "الكمية": 30, "سعر الشراء": 250, "سعر البيع": 320},
        {"الرمز": "2001", "الاسم العربي": "فحص الدم الكامل CBC", "الاسم الإنجليزي": "Complete Blood Count", "النوع": "خدمة مختبر", "الكمية": 999, "سعر الشراء": 0, "سعر البيع": 500}
    ])

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

if 'current_cart' not in st.session_state:
    st.session_state.current_cart = []

if 'documents_archive' not in st.session_state:
    st.session_state.documents_archive = []

# دالة توليد الفاتورة المحدثة (تدعم العربي المعكوس بجانب الإنجليزي)
def generate_pdf_invoice(cart_items, invoice_id, total_amount):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # اختيار الخط بناءً على نجاح تحميل خط Amiri
    font_name = 'Amiri' if font_status else 'Helvetica-Bold'
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    
    normal_style = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=14,
        alignment=2 if font_status else 0  # محاذاة لليمين إذا كان العربي مفعلاً
    )
    
    # عنوان الفاتورة
    story.append(Paragraph("GHASAQ MEDICAL MANAGEMENT SYSTEM", title_style))
    story.append(Spacer(1, 15))
    
    # تفاصيل الفاتورة
    story.append(Paragraph(f"<b>Invoice ID:</b> {invoice_id}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # جدول المنتجات (يحتوي على الاسمين معاً لضمان القراءة الكاملة)
    table_data = [["Item Name (E/A)", "Qty", "Unit Price", "Total (SDG)"]]
    for item in cart_items:
        # دمج الاسم الإنجليزي مع العربي المصلح تقنياً
        display_name = f"{item['الاسم الإنجليزي']} - {format_arabic(item['الاسم العربي'])}" if font_status else item['الاسم الإنجليزي']
        table_data.append([
            Paragraph(display_name, normal_style),
            str(item["الكمية"]),
            f"{item['سعر البيع']:.2f}",
            f"{item['الإجمالي']:.2f}"
        ])
    
    table_data.append([Paragraph(format_arabic("الإجمالي الكلي") if font_status else "Grand Total:", normal_style), "", "", f"{total_amount:.2f}"])
    
    invoice_table = Table(table_data, colWidths=[240, 40, 90, 90])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor("#CBD5E1")),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 30))
    story.append(Paragraph(format_arabic("شكراً لاختياركم خدمات غسق الطبية") if font_status else "Thank you for choosing Ghasaq Medical Services.", title_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- القائمة الجانبية للتنقل ---
st.sidebar.markdown("## 📊 نظام إدارة العمليات (غسق)")
menu = st.sidebar.radio(
    "انتقل إلى:",
    ["🛒 شاشة البيع اليومي (POS)", "📦 إدارة المخزون والإنذارات", "📈 لوحة التحكم والتقارير", "📷 تصوير المستندات والأرشيف"]
)

# ---------------------------------------------
# 1. شاشة البيع اليومي وتوليد الفواتير PDF
# ---------------------------------------------
if menu == "🛒 شاشة البيع اليومي (POS)":
    st.title("🛒 نقطة البيع السريعة (POS)")
    st.subheader("الفاتورة الحالية")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 ابحث عن صنف بالاسم أو الرمز:")
        available_items = st.session_state.inventory
        if search_query:
            available_items = available_items[
                available_items['الاسم العربي'].str.contains(search_query) | available_items['الرمز'].str.contains(search_query) | available_items['الاسم الإنجليزي'].str.contains(search_query, case=False)
            ]
        
        st.write("### الأصناف المتاحة")
        st.dataframe(available_items, use_container_width=True)
    
    with col2:
        st.write("### إضافة صنف للفاتورة")
        if not available_items.empty:
            selected_item_name = st.selectbox("اختر الصنف المتوفر:", available_items['الاسم العربي'].tolist())
            item_row = st.session_state.inventory[st.session_state.inventory['الاسم العربي'] == selected_item_name].iloc[0]
            
            quantity = st.number_input("الكمية المطلوبة:", min_value=1, max_value=int(item_row['الكمية']), value=1)
            
            if st.button("➕ أضف إلى السلة"):
                st.session_state.current_cart.append({
                    "الرمز": item_row['الرمز'],
                    "الاسم العربي": item_row['الاسم العربي'],
                    "الاسم الإنجليزي": item_row['الاسم الإنجليزي'],
                    "الكمية": quantity,
                    "سعر البيع": item_row['سعر البيع'],
                    "الإجمالي": quantity * item_row['سعر البيع']
                })
                st.success(f"تمت إضافة {selected_item_name} إلى السلة")
                st.rerun()

    if st.session_state.current_cart:
        st.write("---")
        st.write("### محتويات الفاتورة الحالية")
        cart_df = pd.DataFrame(st.session_state.current_cart)
        st.dataframe(cart_df[['الرمز', 'الاسم العربي', 'الاسم الإنجليزي', 'الكمية', 'سعر البيع', 'الإجمالي']], use_container_width=True)
        
        total_bill = cart_df['الإجمالي'].sum()
        st.metric(label="إجمالي المطلوب دفعه (جنيه)", value=f"{total_bill:,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 إتمام وحفظ عملية البيع"):
                for index, row in cart_df.iterrows():
                    st.session_state.inventory.loc[st.session_state.inventory['الرمز'] == row['الرمز'], 'الكمية'] -= row['الكمية']
                
                invoice_id = f"INV-{datetime.datetime.now().strftime('%M%S')}"
                st.session_state.sales_history.append({
                    "رقم الفاتورة": invoice_id,
                    "التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "الإجمالي": total_bill,
                    "التفاصيل": st.session_state.current_cart.copy()
                })
                st.success(f"تم حفظ العملية بنجاح برقم: {invoice_id}")
                st.session_state.current_cart = []
                st.rerun()
                
        with c2:
            inv_id = f"INV-{datetime.datetime.now().strftime('%M%S')}"
            pdf_data = generate_pdf_invoice(st.session_state.current_cart, inv_id, total_bill)
            st.download_button(
                label="📄 إصدار وتحميل فاتورة PDF المزدوجة",
                data=pdf_data,
                file_name=f"Ghasaq_{inv_id}.pdf",
                mime="application/pdf"
            )

# ---------------------------------------------
# 2. إدارة المخزون والإنذارات
# ---------------------------------------------
elif menu == "📦 إدارة المخزون والإنذارات":
    st.title("📦 لوحة التحكم بالمخزون والأدوية")
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    low_stock = st.session_state.inventory[(st.session_state.inventory['الكمية'] < 10) & (st.session_state.inventory['النوع'] == 'دواء')]
    if not low_stock.empty:
        st.warning("⚠️ تنبيه: هناك أصناف أوشكت على النفاد في الصيدلية!")
        st.dataframe(low_stock[['الاسم العربي', 'الاسم الإنجليزي', 'الكمية']], use_container_width=True)
        
    st.write("---")
    st.subheader("📥 إضافة وتحديث كميات المنتجات")
    with st.form("inventory_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_code = st.text_input("رمز الصنف:")
            new_name_ar = st.text_input("اسم الدواء (بالعربي):")
            new_name_en = st.text_input("اسم الدواء (بالإنجليزي):")
        with col2:
            new_type = st.selectbox("التصنيف:", ["دواء", "مستلزمات طبي", "خدمة مختبر"])
            new_qty = st.number_input("الكمية المضافة:", min_value=0, value=10)
        with col3:
            new_cost = st.number_input("سعر الشراء (جنيه):", min_value=0, value=100)
            new_price = st.number_input("سعر البيع (جنيه):", min_value=0, value=130)
            
        submit_btn = st.form_submit_button("حفظ وتحديث المستودع")
        if submit_btn:
            if new_code in st.session_state.inventory['الرمز'].values:
                st.session_state.inventory.loc[st.session_state.inventory['الرمز'] == new_code, 'الكمية'] += new_qty
                st.success(f"تم تحديث كمية صنف: {new_name_ar}")
            else:
                new_row = {"الرمز": new_code, "الاسم العربي": new_name_ar, "الاسم الإنجليزي": new_name_en, "النوع": new_type, "الكمية": new_qty, "سعر الشراء": new_cost, "سعر البيع": new_price}
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"تمت إضافة الصنف الجديد: {new_name_ar}")
            st.rerun()

# ---------------------------------------------
# 3. لوحة التحكم والتقارير المالية والرسوم البيانية
# ---------------------------------------------
elif menu == "📈 لوحة التحكم والتقارير":
    st.title("📈 التحليلات والتقارير المالية")
    
    if not st.session_state.sales_history:
        st.info("لا توجد مبيعات مسجلة حتى الآن لإصدار التقارير.")
    else:
        df_sales = pd.DataFrame(st.session_state.sales_history)
        st.metric("إجمالي الإيرادات الحالية (جنيه)", f"{df_sales['الإجمالي'].sum():,.2f}")
        st.write("### حركة المبيعات")
        st.dataframe(df_sales[['رقم الفاتورة', 'التاريخ', 'الإجمالي']], use_container_width=True)
        fig = px.bar(df_sales, x="التاريخ", y="الإجمالي", title="مخطط الإيرادات اليومية والخدمات")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------
# 4. أداة تصوير المستندات والأرشيف الرقمي للمحل
# ---------------------------------------------
elif menu == "📷 تصوير المستندات والأرشيف":
    st.title("📷 أرشفة وتصوير الفواتير والمستندات الورقية")
    doc_title = st.text_input("اسم أو عنوان المستند:")
    img_file = st.camera_input("📸 التقط صورة مباشرة للمستند عبر الكاميرا:")
    uploaded_file = st.file_uploader("📂 أو قم برفع صورة الفاتورة:", type=["jpg", "jpeg", "png"])
    
    final_image = img_file if img_file is not None else uploaded_file
    if final_image is not None and doc_title:
        if st.button("💾 حفظ المستند في الأرشيف السحابي"):
            img = Image.open(final_image)
            st.session_state.documents_archive.append({
                "العنوان": doc_title,
                "التوقيت": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "الصورة": img
            })
            st.success("تم أرشفة المستند بنجاح!")
            st.rerun()
            
    if st.session_state.documents_archive:
        st.write("---")
        st.subheader("🗄️ المستندات المؤرشفة سابقاً")
        for doc_item in st.session_state.documents_archive:
            with st.expander(f"📄 {doc_item['العنوان']} - {doc_item['التوقيت']}"):
                st.image(doc_item['الصورة'], use_container_width=True)
