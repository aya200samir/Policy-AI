import streamlit as st
import requests
from bs4 import BeautifulSoup

# محاولة استيراد المكتبات الثقيلة بأمان
try:
    import google.generativeai as genai
    import tensorflow as tf
    import numpy as np
except ImportError as e:
    st.error(f"حدث خطأ في تحميل المكتبات: {e}. تأكد من ملف requirements.txt")

# --- 1. الإعدادات والجماليات ---
st.set_page_config(page_title="LexGuard AI", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #1a1c24; padding: 20px; border-radius: 10px; border-right: 5px solid #daa520; }
    h1, h2 { color: #daa520 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الربط بمفتاح جيميناي الخاص بكِ ---
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. وظائف النظام ---
def scrape_policy(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text[:4000]
    except: return None

# --- 4. واجهة التطبيق ---
st.title("⚖️ LexGuard AI | خبير الامتثال الذكي")
url_input = st.text_input("أدخل رابط سياسة الخصوصية:")

if st.button("بدء التحليل"):
    if url_input:
        with st.spinner("جاري التحليل..."):
            content = scrape_policy(url_input)
            if content:
                # التحليل باستخدام جيميناي (RAG)
                def analyze(law_type):
                    prompt = f"حلل السياسة التالية بناءً على {law_type}: {content}. اذكر المخالفات باللغة العربية ودرجة الامتثال."
                    return gemini_model.generate_content(prompt).text

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇬 القانون المصري")
                    st.write(analyze("قانون 151 لسنة 2020 المصري"))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇺 القانون الأوروبي")
                    st.write(analyze("GDPR"))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("تعذر الوصول للموقع.")
