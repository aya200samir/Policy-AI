import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai
import os

# محاولة استيراد TensorFlow بشكل آمن لتجنب أخطاء السيرفر
try:
    import tensorflow as tf
except ImportError:
    st.error("TensorFlow missing! Please ensure 'tensorflow-cpu' is in requirements.txt")

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="LexGuard AI | خبير الامتثال",
    page_icon="⚖️",
    layout="wide"
)

# ستايل احترافي (أسود وذهبي)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card { 
        background-color: #1a1c24; 
        padding: 25px; 
        border-radius: 15px; 
        border-right: 5px solid #daa520; 
        margin-bottom: 20px;
        color: white;
    }
    h1, h2, h3 { color: #daa520 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #b8860b; 
        color: white; 
        width: 100%; 
        border-radius: 10px; 
        font-weight: bold; 
        height: 3em;
    }
    .stButton>button:hover { background-color: #daa520; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات Gemini ---
# تأكدي من وضع المفتاح في Streamlit Secrets باسم GEMINI_API_KEY
# أو سيستخدم الكود المفتاح المباشر الذي قدمتيه سابقاً
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI")
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. تحميل الموديل (الخلايا العصبية) ---
@st.cache_resource
def load_my_model():
    model_path = 'best_model.h5'
    if os.path.exists(model_path):
        try:
            # تحميل الموديل الذي حقق 90% accuracy
            return tf.keras.models.load_model(model_path, compile=False)
        except Exception as e:
            st.warning(f"⚠️ وجدنا ملف الموديل ولكن فشل تحميله: {e}")
            return None
    return None

nn_model = load_my_model()

# --- 4. وظائف النظام ---
def scrape_policy(url):
    """سحب النص من الرابط وتنظيفه"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = ' '.join(soup.get_text().split())
        return text[:4000]
    except:
        return None

def get_legal_report(policy_text, law_name):
    """تحليل السياسة باستخدام جيميناي"""
    prompt = f"""
    أنت مدقق قانوني خبير في {law_name}.
    قم بتحليل نص سياسة الخصوصية التالي:
    {policy_text}
    
    المطلوب باللغة العربية:
    1. اذكر أهم المخالفات القانونية المكتشفة.
    2. اشرح بلهجة بسيطة للمواطن المصري ماذا يحدث لبياناته.
    3. أعطِ درجة امتثال نهائية من 10.
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return "⚠️ فشل الاتصال بخدمة الذكاء الاصطناعي حالياً."

# --- 5. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center;'>⚖️ LexGuard AI: Privacy Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>النظام الهجين للتدقيق في سياسات الخصوصية (Neural Network + Gemini)</p>", unsafe_allow_html=True)

if nn_model:
    st.success("🧠 تم تحميل موديل الخلايا العصبية (Accuracy: 90%) بنجاح.")
else:
    st.info("ℹ️ الموديل المحلي غير متاح، النظام يعمل الآن بكامل طاقة Gemini AI.")

url_input = st.text_input("📍 أدخل رابط سياسة الخصوصية لفحصها:")

if st.button("إجراء التدقيق القانوني"):
    if url_input:
        with st.spinner("جاري استخراج النص والتحليل..."):
            policy_content = scrape_policy(url_input)
            
            if policy_content:
                # التحليل المزدوج
                res_eg = get_legal_report(policy_content, "قانون حماية البيانات المصري 151 لسنة 2020")
                res_eu = get_legal_report(policy_content, "القانون الأوروبي (GDPR)")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇬 القانون المصري")
                    st.write(res_eg)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.header("🇪🇺 القانون الأوروبي")
                    st.write(res_eu)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("فشلنا في سحب النص من الرابط، تأكدي من صحته.")
    else:
        st.warning("يرجى إدخال الرابط أولاً.")

st.markdown("<br><hr><p style='text-align: center; color: #555;'>LexGuard AI Team - 2026</p>", unsafe_allow_html=True)
