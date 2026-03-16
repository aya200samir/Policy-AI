import streamlit as st
import google.generativeai as genai
import tensorflow as tf
import requests
from bs4 import BeautifulSoup
import numpy as np

# 1. إعدادات الأمان للمفتاح
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("API Key missing! Please add it to Streamlit Secrets.")

# 2. تحميل الموديل الجاهز (الملف الذي رفعتيه)
@st.cache_resource
def load_lexguard_model():
    return tf.keras.models.load_model('best_model.h5')

# 3. دالة سحب النصوص
def scrape_policy(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text if len(text) > 100 else "Could not find enough text."
    except:
        return "Error fetching URL."

# 4. الواجهة الاحترافية
st.set_page_config(page_title="LexGuard AI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #daa520;'>⚖️ LexGuard AI: Privacy Compliance</h1>", unsafe_allow_html=True)

url_input = st.text_input("أدخل رابط سياسة الخصوصية لفحصها:")

if st.button("بدء التحليل العميق"):
    if url_input:
        with st.spinner("جاري استخراج البيانات وتحليلها قانونياً..."):
            # سحب النص
            policy_text = scrape_policy(url_input)
            
            # الربط مع جيميناي للتحليل
            def get_analysis(region_name):
                prompt = f"Analyze this policy against {region_name} data laws: {policy_text[:3000]}. Provide violations and a score out of 10 in Arabic."
                return gemini_model.generate_content(prompt).text

            res_eg = get_analysis("Egyptian Law 151/2020")
            res_eu = get_analysis("EU GDPR")

            # عرض النتائج
            col1, col2 = st.columns(2)
            with col1:
                st.info("🇪🇬 التقرير المصري")
                st.write(res_eg)
            with col2:
                st.info("🇪🇺 التقرير الأوروبي")
                st.write(res_eu)
    else:
        st.warning("من فضلك أدخل الرابط أولاً.")
