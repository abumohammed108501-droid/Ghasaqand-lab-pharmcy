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
    .stApp { background-color: #F8FAFC; }
    h1 { color: #0F172A !important; font-weight: 700; }
    h3 { color: #1E3A8A !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; color: white !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-right: 5px solid #0EA5E9; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True) # تم تصحيح الخطأ هنا

# دالة ذكية لتحميل خط عربي
@st.cache_resource
def setup_arabic_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        response = requests.get(font_url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    pdfmetrics.registerFont(TTFont('Amiri', font_path))
    return True

font_status = setup_arabic_font()

# باقي الكود كما هو...
# (تأكد من لصق باقي الكود الخاص بـ POS والمخزون هنا)
