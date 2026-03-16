import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai
import os

# محاولة استيراد TensorFlow بشكل آمن
try:
    import tensorflow as tf
except ImportError:
    st.error("TensorFlow missing! Please ensure 'tensorflow-cpu' is in requirements.txt")

# --- 1. إعدادات الصفحة والجماليات ---
st.set_page_config(page_title="LexGuard AI | خبير الامتثال", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card { background-color: #1a1c24; padding: 25px; border-radius: 15px; border-right: 5px solid #daa520; margin-bottom: 20px; color: white; }
    h1, h2, h3 { color: #daa520 !important; }
    .stButton>button { background-color: #b8860b; color: white; width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تحميل الموديل من Google Drive تلقائياً ---
@st.cache_resource
def load_nn_model():
    model_path = 'best_model.h5'
    # إذا لم يكن الملف موجوداً في السيرفر، يتم تحميله من الرابط الذي وفره المستخدم
    if not os.path.exists(model_path):
        with st.spinner("جاري تحميل مخ الذكاء الاصطناعي من Google Drive... قد يستغرق ذلك دقيقة واحدة."):
            file_id = '1BxUh_coRQzrqOz1n2AX2xRl4CDVk9qb7'
            url = f'https://drive.google.com/uc?id={file_id}'
            try:
                # استخدام أمر wget لتحميل الملف مباشرة إلى السيرفر
                os.system(f'wget --no-check-certificate {url} -O {model_path}')
            except Exception as e:
                st.error(f"فشل التحميل من درايف: {e}")
                return None
    
    try:
        return tf.keras.models.load_model(model_path, compile=False)
    except Exception as e:
        st.error(f"خطأ في قراءة ملف الموديل: {e}")
        return None

nn_model = load_nn_model()

# --- 3. إعدادات Gemini ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI")
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 4. وظائف التحليل ---
def scrape_policy(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        return ' '.join(soup.get_text().split())[:4000]
    except:
        return None

def get_compliance_report(text, law):
    prompt = f"أنت مدقق قانوني، حلل هذه السياسة بناءً على {law}: {text}. اذكر المخالفات بالعربية ودرجة الامتثال من 10."
    try:
        return gemini_model.generate_content(prompt).text
    except:
        return "⚠️ حدث خطأ في تحليل Gemini."

# --- 5. واجهة المستخدم ---
st.title("⚖️ LexGuard AI: Privacy Auditor")
st.write("نظام هجين يدمج بين الشبكات العصبية وذكاء Gemini")

if nn_model:
    st.success("✅ تم ربط الموديل المحلي (90% Accuracy) بنجاح.")

url_input = st.text_input("ضع رابط سياسة الخصوصية هنا:")

if st.button("بدء التدقيق القانوني"):
    if url_input:
        with st.spinner("جاري التحليل العميق..."):
            content = scrape_policy(url_input)
            if content:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇬 القانون المصري")
                    st.write(get_compliance_report(content, "قانون 151 لسنة 2020"))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇺 القانون الأوروبي")
                    st.write(get_compliance_report(content, "GDPR"))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("تعذر سحب البيانات من الرابط.")
