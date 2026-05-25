import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
import datetime

# إعداد الصفحة
st.set_page_config(page_title="نظام غسق الطبي", layout="wide")

# كود الواجهة الطبية (تم دمجه بشكل سليم)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1 { color: #0F172A !important; }
    .metric-card {
        background-color: white; 
        padding: 20px; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-right: 5px solid #0EA5E9;
    }
    </style>
""", unsafe_allow_html=True)

# العنوان
st.title("💊 نظام غسق الطبي")

# إضافة بسيطة للتأكد من أن كل شيء يعمل
st.markdown('<div class="metric-card">تم تفعيل النمط الطبي بنجاح!</div>', unsafe_allow_html=True)

st.write("الآن النظام يعمل مع الواجهة المحسنة.")
