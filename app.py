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

st.set_page_config(page_title="نظام غسق", layout="wide")

# تصحيح كود الـ CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    </style>
""", unsafe_allow_html=True)

# تهيئة بسيطة للتأكد من عمل النظام
st.title("نظام غسق الطبي")
st.write("تم استعادة النظام بنجاح. النظام يعمل الآن.")
