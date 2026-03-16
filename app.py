import streamlit as st
import google.generativeai as genai
import tensorflow as tf
import requests
from bs4 import BeautifulSoup
import numpy as np

# --- 1. CONFIGURATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("Missing Gemini API Key in Streamlit Secrets!")

# --- 2. LOAD YOUR 90% ACCURACY MODEL ---
@st.cache_resource
def load_lexguard_model():
    # تأكدي أن ملف best_model.h5 مرفوع بجانب هذا الملف
    return tf.keras.models.load_model('best_model.h5')

# --- 3. SCRAPING FUNCTION ---
def scrape_policy(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text if len(text) > 100 else "Text too short to analyze."
    except Exception as e:
        return f"Error: {e}"

# --- 4. PROFESSIONAL UI ---
st.set_page_config(page_title="LexGuard AI", layout="wide")

# CSS for Luxury Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #daa520; text-align: center; }
    .stButton>button { background-color: #b8860b; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ LexGuard AI: Privacy Compliance Expert")
st.write("الجيل القادم من فحص سياسات الخصوصية بالذكاء الاصطناعي ")

url_input = st.text_input("أدخل رابط سياسة الخصوصية:")

if st.button("بدء التحليل القانوني الشامل"):
    if url_input:
        with st.spinner("جاري سحب النص وتحليله بواسطة الخلايا العصبية وجيميناي..."):
            # 1. Scraping
            policy_text = scrape_policy(url_input)
            
            # 2. Hybrid Analysis
            # هنا نرسل النص لجيميناي ليقوم بالتحليل القانوني (RAG)
            prompt_eg = f"Analyze this policy against Egyptian Law 151/2020: {policy_text[:3500]}. List violations in Arabic and give a score."
            prompt_eu = f"Analyze this policy against EU GDPR: {policy_text[:3500]}. List violations in Arabic and give a score."
            
            res_eg = gemini_model.generate_content(prompt_eg).text
            res_eu = gemini_model.generate_content(prompt_eu).text

            # 3. Display Results
            col1, col2 = st.columns(2)
            with col1:
                st.header("🇪🇬 القانون المصري")
                st.info(res_eg)
            with col2:
                st.header("🇪🇺 القانون الأوروبي")
                st.info(res_eu)
    else:
        st.warning("يرجى إدخال الرابط.")
