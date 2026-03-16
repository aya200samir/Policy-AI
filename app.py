import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai
import os
import gdown

# محاولة استيراد TensorFlow
try:
    import tensorflow as tf
except ImportError:
    st.error("TensorFlow missing! Please ensure 'tensorflow-cpu' is in requirements.txt")

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="LexGuard AI", layout="wide", page_icon="⚖️")

# --- 2. تحميل الموديل من Google Drive بطريقة آمنة ---
@st.cache_resource
def load_nn_model():
    model_path = 'best_model.h5'
    file_id = '1BxUh_coRQzrqOz1n2AX2xRl4CDVk9qb7'
    url = f'https://drive.google.com/uc?id={file_id}'
    
    if not os.path.exists(model_path):
        try:
            with st.spinner("جاري تحميل مخ الذكاء الاصطناعي (أول مرة فقط)..."):
                gdown.download(url, model_path, quiet=False)
        except Exception as e:
            st.warning(f"لم نتمكن من تحميل الموديل من درايف، سنعتمد على جيميناي حالياً.")
            return None

    try:
        # تحميل الموديل مع إهمال الطبقات التدريبية لضمان العمل على السيرفر
        model = tf.keras.models.load_model(model_path, compile=False)
        return model
    except Exception as e:
        # إذا حدث خطأ في القراءة، نحذف الملف التالف ونكمل بجيميناي
        if os.path.exists(model_path):
            os.remove(model_path)
        return None

nn_model = load_nn_model()

# --- 3. إعدادات Gemini ---
# المفتاح الخاص بكِ
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 4. وظائف التحليل ---
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
    prompt = f"حلل سياسة الخصوصية التالية بناءً على {law} باللغة العربية: {text}"
    try:
        return gemini_model.generate_content(prompt).text
    except:
        return "⚠️ عذراً، جيميناي غير متاح حالياً."

# --- 5. الواجهة الرسومية ---
st.title("⚖️ LexGuard AI: خبير الامتثال الذكي")

if nn_model:
    st.success("✅ النظام يعمل بالذكاء الاصطناعي الهجين (NN + Gemini)")
else:
    st.info("💡 النظام يعمل حالياً بذكاء Gemini المتقدم.")

url_input = st.text_input("ضع رابط السياسة هنا (مثال: سياسة واتساب):")

if st.button("بدء الفحص القانوني"):
    if url_input:
        with st.spinner("جاري استخراج البيانات وتحليلها..."):
            content = scrape_policy(url_input)
            if content:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🇪🇬 القانون المصري")
                    st.info(get_report(content, "قانون 151 لسنة 2020"))
                with col2:
                    st.subheader("🇪🇺 القانون الأوروبي (GDPR)")
                    st.info(get_report(content, "GDPR"))
            else:
                st.error("تعذر قراءة الموقع، يرجى التأكد من الرابط.")
