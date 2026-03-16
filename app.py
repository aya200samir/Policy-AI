import streamlit as st
import os
import subprocess
import sys

# وظيفة لتثبيت المكتبات الناقصة تلقائياً
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# محاولة استيراد gdown، وإذا فشلت يتم تثبيتها فوراً
try:
    import gdown
except ImportError:
    install('gdown')
    import gdown

import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="LexGuard AI", layout="wide", page_icon="⚖️")

# --- 2. تحميل الموديل من Google Drive ---
@st.cache_resource
def load_nn_model():
    model_path = 'best_model.h5'
    file_id = '1BxUh_coRQzrqOz1n2AX2xRl4CDVk9qb7'
    url = f'https://drive.google.com/uc?id={file_id}'
    
    if not os.path.exists(model_path):
        try:
            with st.spinner("جاري تهيئة نظام الذكاء الاصطناعي..."):
                # استخدام gdown للتحميل
                gdown.download(url, model_path, quiet=False)
        except Exception as e:
            return None

    try:
        import tensorflow as tf
        return tf.keras.models.load_model(model_path, compile=False)
    except:
        return None

nn_model = load_nn_model()

# --- 3. إعدادات Gemini ---
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 4. واجهة التطبيق ---
st.title("⚖️ LexGuard AI: Privacy Auditor")

if nn_model:
    st.success("✅ تم ربط الموديل الخاص بكِ بنجاح.")
else:
    st.info("💡 يعمل النظام حالياً عبر ذكاء Gemini السحابي.")

url_input = st.text_input("أدخل رابط سياسة الخصوصية لفحصها:")

if st.button("بدء الفحص"):
    if url_input:
        with st.spinner("جاري التحليل..."):
            try:
                res = requests.get(url_input, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                text = ' '.join(soup.get_text().split())[:4000]
                
                prompt = f"حلل سياسة الخصوصية هذه بالعربية وفق القانون المصري 151 والقانون الأوروبي: {text}"
                report = gemini_model.generate_content(prompt).text
                
                st.markdown("### التقرير القانوني")
                st.write(report)
            except:
                st.error("تعذر الوصول للرابط.")
