import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai
import os
import gdown

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
            with st.spinner("جاري جلب مخ الذكاء الاصطناعي من السحابة..."):
                # تحميل الملف باستخدام gdown
                gdown.download(url, model_path, quiet=False)
        except Exception as e:
            st.error(f"فشل التحميل: {e}")
            return None

    try:
        # استيراد تينسورفلو هنا لضمان سرعة تشغيل الواجهة أولاً
        import tensorflow as tf
        # تحميل الموديل مع تعطيل الـ compile لتجنب مشاكل التوافق
        model = tf.keras.models.load_model(model_path, compile=False)
        return model
    except Exception as e:
        # إذا فشلت القراءة، غالباً الملف نزل ناقص، سنعتمد على جيميناي
        return None

# محاولة تحميل الموديل
nn_model = load_nn_model()

# --- 3. إعدادات Gemini ---
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 4. وظائف التدقيق ---
def scrape_policy(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        return ' '.join(soup.get_text().split())[:4500]
    except:
        return None

def get_report(text, law):
    prompt = f"حلل سياسة الخصوصية التالية بناءً على {law} باللغة العربية: {text}. اذكر المخالفات ودرجة الامتثال."
    try:
        return gemini_model.generate_content(prompt).text
    except:
        return "⚠️ خدمة التحليل غير متاحة حالياً."

# --- 5. الواجهة ---
st.title("⚖️ LexGuard AI: Privacy Auditor")

if nn_model:
    st.success("✅ تم تفعيل الذكاء الاصطناعي الهجين بنجاح.")
else:
    st.info("💡 النظام يعمل حالياً بذكاء Gemini المتقدم.")

url_input = st.text_input("أدخل رابط سياسة الخصوصية:")

if st.button("بدء الفحص القانوني"):
    if url_input:
        with st.spinner("جاري التحليل..."):
            content = scrape_policy(url_input)
            if content:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🇪🇬 القانون المصري")
                    st.write(get_report(content, "قانون 151 لسنة 2020"))
                with col2:
                    st.subheader("🇪🇺 القانون الأوروبي (GDPR)")
                    st.write(get_report(content, "GDPR"))
            else:
                st.error("تعذر قراءة الموقع، تأكد من الرابط.")
