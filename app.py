import streamlit as st
import google.generativeai as genai
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import requests
from bs4 import BeautifulSoup
import numpy as np

# --- إعدادات جيميناي ---
# استخدام Secrets للحفاظ على أمان المفتاح عند الرفع على GitHub
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- تحميل الموديل الذي حقق 90% ---
@st.cache_resource # لضمان تحميل الموديل مرة واحدة فقط لتسريع التطبيق
def load_my_model():
    return tf.keras.models.load_model('best_model.h5')

nn_model = load_my_model()

# --- دالة سحب البيانات من الروابط ---
def scrape_policy(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])

# --- واجهة المستخدم (Streamlit UI) ---
st.set_page_config(page_title="LexGuard AI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #daa520;'>⚖️ LexGuard AI: Privacy Compliance Expert</h1>", unsafe_allow_html=True)

url_input = st.text_input("أدخل رابط سياسة الخصوصية:")

if st.button("تحليل الامتثال"):
    with st.spinner("جاري التحليل..."):
        # 1. سحب النص
        policy_text = scrape_policy(url_input)
        
        # 2. التحليل بواسطة جيميناي (المصري والأوروبي)
        prompt_eg = f"Analyze this policy against Egyptian Law 151/2020: {policy_text[:3000]}"
        prompt_eu = f"Analyze this policy against EU GDPR: {policy_text[:3000]}"
        
        res_eg = gemini_model.generate_content(prompt_eg).text
        res_eu = gemini_model.generate_content(prompt_eu).text
        
        # 3. عرض النتائج بشكل فخم
        col1, col2 = st.columns(2)
        with col1:
            st.info("🇪🇬 التقرير المصري")
            st.write(res_eg)
        with col2:
            st.info("🇪🇺 التقرير الأوروبي")
            st.write(res_eu)
