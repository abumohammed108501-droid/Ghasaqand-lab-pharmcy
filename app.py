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

# --- لمسة التصميم الطبي الاحترافي (CSS) ---
st.markdown("""
    <style>
    /* تعديل الخلفية العامة ولون النصوص */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* تنسيق العناوين الرئيسية */
    h1 {
        color: #0F172A !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    h3 {
        color: #1E3A8A !important; /* أزرق طبي عميق */
    }
    
    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important; /* كحلي غامق فخم */
        color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* بطاقات العرض الرقمية (Cards) */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-right: 5px solid #0EA5E9; /* مؤشر أزرق سماوي */
        margin-bottom: 15px;
    }
    
    /* تحسين مظهر الجداول */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    </style>
""", unsafe html=True)


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
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# تهيئة قاعدة البيانات المؤقتة في الذاكرة
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

# دالة توليد الفاتورة PDF
def generate_pdf_invoice(cart_items, invoice_id, total_amount):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    font_name = 'Amiri' if font_status else 'Helvetica-Bold'
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"), # اللون الأزرق الطبي للفاتورة
        alignment=1
    )
    
    normal_style = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=14,
        alignment=2 if font_status else 0
    )
    
    story.append(Paragraph("GHASAQ MEDICAL MANAGEMENT SYSTEM", title_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"<b>Invoice ID:</b> {invoice_id}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    table_data = [["Item Name (E/A)", "Qty", "Unit Price", "Total (SDG)"]]
    for item in cart_items:
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")), # ترويسة الفاتورة زرقاء متناسقة مع الهوية الجديدة
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor("#CBD5E1")),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 30))
    story.append(Paragraph(format_arabic("شكراً لاختياركم خدمات غسق الطبية") if font_status else "Thank you for choosing Ghasaq Medical Services.", title_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- القائمة الجانبية للتنقل ---
st.sidebar.markdown("<h2 style='color:white; text-align:center;'>💊 نظام غسق الطبي</h2>", unsafe_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "انتقل إلى الأقسام:",
    ["🛒 شاشة البيع اليومي (POS)", "📦 إدارة المخزون والإنذارات", "📈 لوحة التحكم والتقارير", "📷 تصوير المستندات والأرشيف"]
)

# ---------------------------------------------
# 1. شاشة البيع اليومي وتوليد الفواتير PDF
# ---------------------------------------------
if menu == "🛒 شاشة البيع اليومي (POS)":
    st.title("🛒 نقطة البيع السريعة والخدمات")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔍 البحث السريع عن الأصناف")
        search_query = st.text_input("ادخل اسم الدواء، الخدمة، أو رمز الباركود:")
        available_items = st.session_state.inventory
        if search_query:
            available_items = available_items[
                available_items['الاسم العربي'].str.contains(search_query) | available_items['الرمز'].str.contains(search_query) | available_items['الاسم الإنجليزي'].str.contains(search_query, case=False)
            ]
        
        st.dataframe(available_items, use_container_width=True)
    
    with col2:
        st.markdown("### ➕ الصرف وإضافة الفاتورة")
        if not available_items.empty:
            selected_item_name = st.selectbox("اختر الصنف المطلوب صرفه:", available_items['الاسم العربي'].tolist())
            item_row = st.session_state.inventory[st.session_state.inventory['الاسم العربي'] == selected_item_name].iloc[0]
            
            quantity = st.number_input("الكمية المطلوبة:", min_value=1, max_value=int(item_row['الquantية'] if 'الكمية' in item_row else item_row['الكمية']), value=1)
            
            if st.button("➕ إدراج في سلة البيع", use_container_width=True):
                st.session_state.current_cart.append({
                    "الرمز": item_row['الرمز'],
                    "الاسم العربي": item_row['الاسم العربي'],
                    "الاسم الإنجليزي": item_row['الاسم الإنجليزي'],
                    "الكمية": quantity,
                    "سعر البيع": item_row['سعر البيع'],
                    "الإجمالي": quantity * item_row['سعر البيع']
                })
                st.success(f"تم إدراج {selected_item_name} بنجاح.")
                st.rerun()

    if st.session_state.current_cart:
        st.markdown("---")
        st.subheader("📋 مراجعة وتدقيق الفاتورة الحالية")
        cart_df = pd.DataFrame(st.session_state.current_cart)
        st.dataframe(cart_df[['الرمز', 'الاسم العربي', 'الاسم الإنجليزي', 'الكمية', 'سعر البيع', 'الإجمالي']], use_container_width=True)
        
        total_bill = cart_df['الإجمالي'].sum()
        
        # عرض الإجمالي داخل بطاقة طبية متميزة بصرياً
        st.markdown(f"""
            <div class="metric-card">
                <span style="color: #64748B; font-size: 14px; font-weight: 600;">إجمالي المطلوب سداده</span>
                <h2 style="color: #0EA5E9; margin: 5px 0 0 0; font-size: 32px;">{total_bill:,.2f} <span style="font-size: 18px;">جنيه سوداني</span></h2>
            </div>
        """, unsafe_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 ترحيل وحفظ العملية بالخزينة", use_container_width=True, type="primary"):
                for index, row in cart_df.iterrows():
                    st.session_state.inventory.loc[st.session_state.inventory['الرمز'] == row['الرمز'], 'الكمية'] -= row['الكمية']
                
                invoice_id = f"INV-{datetime.datetime.now().strftime('%M%S')}"
                st.session_state.sales_history.append({
                    "رقم الفاتورة": invoice_id,
                    "التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "الإجمالي": total_bill,
                    "التفاصيل": st.session_state.current_cart.copy()
                })
                st.success(f"تم ترحيل العملية لحسابات الأرباح برقم: {invoice_id}")
                st.session_state.current_cart = []
                st.rerun()
                
        with c2:
            inv_id = f"INV-{datetime.datetime.now().strftime('%M%S')}"
            pdf_data = generate_pdf_invoice(st.session_state.current_cart, inv_id, total_bill)
            st.download_button(
                label="📄 طباعة وإصدار فاتورة الـ PDF الطبية",
                data=pdf_data,
                file_name=f"Ghasaq_{inv_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ---------------------------------------------
# 2. إدارة المخزون والإنذارات
# ---------------------------------------------
elif menu == "📦 إدارة المخزون والإنذارات":
    st.title("📦 مستودع الأدوية والمستلزمات الطبية")
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    low_stock = st.session_state.inventory[(st.session_state.inventory['الكمية'] < 10) & (st.session_state.inventory['النوع'] == 'دواء')]
    if not low_stock.empty:
        st.markdown("""
            <div style="background-color: #FEF2F2; border-right: 5px solid #EF4444; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #991B1B; margin: 0;">⚠️ تنبيه النفاذ الوشيك للمخزون</h4>
                <p style="color: #7F1D1D; margin: 5px 0 0 0; font-size: 14px;">يرجى مراجعة الأصناف التالية وإبلاغ الموردين بالخرطوم فوراً لتأمين الطلبيات.</p>
            </div>
        """, unsafe_html=True)
        st.dataframe(low_stock[['الاسم العربي', 'الاسم الإنجليزي', 'الكمية']], use_container_width=True)
        
    st.markdown("---")
    st.subheader("📥 مدخلات المستودع وتحديث أسعار الصرف")
    with st.form("inventory_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_code = st.text_input("رمز الصنف (باركود):")
            new_name_ar = st.text_input("الاسم التجاري (عربي):")
            new_name_en = st.text_input("الاسم العلمي/التجاري (إنجليزي):")
        with col2:
            new_type = st.selectbox("تصنيف الصنف العلمي:", ["دواء", "مستلزمات طبي", "خدمة مختبر"])
            new_qty = st.number_input("الكمية الواردة:", min_value=0, value=10)
        with col3:
            new_cost = st.number_input("تكلفة الشراء (جنيه):", min_value=0, value=100)
            new_price = st.number_input("سعر الجمهور (جنيه):", min_value=0, value=130)
            
        submit_btn = st.form_submit_button("اعتماد وتحديث بيانات المستودع", use_container_width=True)
        if submit_btn:
            if new_code in st.session_state.inventory['الرمز'].values:
                st.session_state.inventory.loc[st.session_state.inventory['الرمز'] == new_code, 'الكمية'] += new_qty
                st.success(f"تمت إضافة الكمية الموردة لـ: {new_name_ar}")
            else:
                new_row = {"الرمز": new_code, "الاسم العربي": new_name_ar, "الاسم الإنجليزي": new_name_en, "النوع": new_type, "الكمية": new_qty, "سعر الشراء": new_cost, "سعر البيع": new_price}
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"تم قيد الصنف الطبي الجديد بالمنظومة: {new_name_ar}")
            st.rerun()

# ---------------------------------------------
# 3. لوحة التحكم والتقارير المالية والرسوم البيانية
# ---------------------------------------------
elif menu == "📈 لوحة التحكم والتقارير":
    st.title("📈 لوحة التحليلات والتقارير المالية")
    
    if not st.session_state.sales_history:
        st.info("لا توجد عمليات مبيعات مقيدة اليوم لإصدار التقارير الحسابية.")
    else:
        df_sales = pd.DataFrame(st.session_state.sales_history)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div class="metric-card" style="border-right-color: #10B981;">
                    <span style="color: #64748B; font-size: 14px; font-weight: 600;">📊 مجمل الدخل الحركي</span>
                    <h2 style="color: #10B981; margin: 5px 0 0 0; font-size: 30px;">{df_sales['الإجمالي'].sum():,.2f} <span style="font-size: 16px;">جنيه</span></h2>
                </div>
            """, unsafe_html=True)
        with c2:
            st.markdown(f"""
                <div class="metric-card" style="border-right-color: #6366F1;">
                    <span style="color: #64748B; font-size: 14px; font-weight: 600;">🧾 الفواتير الكلية الصادرة</span>
                    <h2 style="color: #6366F1; margin: 5px 0 0 0; font-size: 30px;">{len(df_sales)} <span style="font-size: 16px;">فواتير مسجلة</span></h2>
                </div>
            """, unsafe_html=True)
            
        st.write("### سجل المبيعات والتدفق النقدي ورقة ورقة")
        st.dataframe(df_sales[['رقم الفاتورة', 'التاريخ', 'الإجمالي']], use_container_width=True)
        fig = px.bar(df_sales, x="التاريخ", y="الإجمالي", title="حجم الإيرادات والمصروفات اليومية المتدفقة", color_discrete_sequence=['#0EA5E9'])
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------
# 4. أداة تصوير المستندات والأرشيف الرقمي للمحل
# ---------------------------------------------
elif menu == "📷 تصوير المستندات والأرشيف":
    st.title("📷 الحفظ والأرشفة الرقمية للطلبيات وفواتير الموردين")
    st.write("أداة الحماية من الفقدان المالي والورقي؛ صوّر فواتير شركات التوزيع واحتفظ بها سحابياً.")
    
    doc_title = st.text_input("عنوان أو تفاصيل السند الورقي لتسهيل الفرز المالي لاحقاً:")
    img_file = st.camera_input("📸 التقط صورة حية للفاتورة عبر كاميرا الهاتف والكمبيوتر:")
    uploaded_file = st.file_uploader("📂 أو ارفع صورة المستند من الأستوديو:", type=["jpg", "jpeg", "png"])
    
    final_image = img_file if img_file is not None else uploaded_file
    if final_image is not None and doc_title:
        if st.button("💾 تشفير وأرشفة المستند سحابياً", use_container_width=True, type="primary"):
            img = Image.open(final_image)
            st.session_state.documents_archive.append({
                "العنوان": doc_title,
                "التوقيت": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "الصورة": img
            })
            st.success("تم الحفظ والأرشفة في الأرشيف السحابي لغسق بنجاح تام.")
            st.rerun()
            
    if st.session_state.documents_archive:
        st.markdown("---")
        st.subheader("🗄️ الأرشيف الرقمي المحفوظ (سجلات الخرطوم)")
        for doc_item in st.session_state.documents_archive:
            with st.expander(f"📄 {doc_item['العنوان']} - التوقيت: {doc_item['التوقيت']}"):
                st.image(doc_item['الصورة'], use_container_width=True)
