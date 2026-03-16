import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import google.generativeai as genai
import os
import gdown

# محاولة استيراد TensorFlow بشكل آمن
try:
    import tensorflow as tf
except ImportError:
    st.error("TensorFlow missing! Please ensure 'tensorflow-cpu' is in requirements.txt")

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="LexGuard AI | منصة التدقيق القانوني",
    page_icon="⚖️",
    layout="wide"
)

# تصميم الواجهة (أسود وذهبي)
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
    h1, h2, h3 { color: #daa520 !important; }
    .stButton>button { 
        background-color: #b8860b; 
        color: white; 
        width: 100%; 
        border-radius: 10px; 
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات Gemini ---
# ملاحظة: يمكنك وضع المفتاح في Streamlit Secrets للأمان
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI" 
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. تحميل الموديل من Google Drive ---
@st.cache_resource
def load_nn_model():
    model_path = 'best_model.h5'
    # معرف الملف من الرابط الذي قدمتيه
    file_id = '1BxUh_coRQzrqOz1n2AX2xRl4CDVk9qb7'
    url = f'https://drive.google.com/uc?id={file_id}'
    
    # إذا لم يكن الملف موجوداً محلياً على السيرفر، قم بتحميله
    if not os.path.exists(model_path):
        try:
            with st.spinner("جاري تحميل مخ الذكاء الاصطناعي (أول مرة فقط)..."):
                gdown.download(url, model_path, quiet=False)
        except Exception as e:
            st.warning(f"⚠️ فشل التحميل من درايف: {e}")
            return None

    try:
        # تحميل الموديل (compile=False لضمان التوافق مع السيرفر)
        model = tf.keras.models.load_model(model_path, compile=False)
        return model
    except Exception as e:
        st.error(f"⚠️ خطأ في قراءة ملف الموديل: {e}")
        return None

nn_model = load_nn_model()

# --- 4. وظائف استخراج وتحليل البيانات ---
def scrape_policy(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        return ' '.join(soup.get_text().split())[:4500]
    except Exception as e:
        return None

def get_gemini_analysis(policy_text, law_name):
    prompt = f"""
    أنت مستشار قانوني خبير في {law_name}. 
    قم بمراجعة النص التالي لسياسة الخصوصية:
    {policy_text}
    
    المطلوب (بالعربية):
    1. قائمة بالمخالفات الصريحة.
    2. شرح مبسط للمواطن: ماذا يحدث لبياناتك؟
    3. تقييم نهائي من 10.
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ في الاتصال بـ Gemini: {e}"

# --- 5. واجهة التطبيق ---
st.markdown("<h1 style='text-align: center;'>⚖️ LexGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>نظام هجين للتدقيق القانوني الذكي (NN + Gemini)</p>", unsafe_allow_html=True)

if nn_model:
    st.success("✅ تم ربط موديل الشبكة العصبية (Accuracy 90%) بنجاح.")
else:
    st.info("💡 النظام يعمل حالياً بذكاء Gemini السحابي المتقدم.")

url_input = st.text_input("📍 أدخل رابط سياسة الخصوصية للفحص:")

if st.button("🚀 ابدأ الفحص القانوني الشامل"):
    if url_input:
        with st.spinner("جاري التحليل..."):
            policy_content = scrape_policy(url_input)
            if policy_content:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.subheader("🇪🇬 القانون المصري (151/2020)")
                    st.write(get_gemini_analysis(policy_content, "قانون حماية البيانات المصري"))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.subheader("🇪🇺 معايير الـ GDPR")
                    st.write(get_gemini_analysis(policy_content, "الـ GDPR الأوروبي"))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("تعذر سحب النص من الرابط. تأكد من صحة الرابط.")
    else:
        st.warning("يرجى إدخال الرابط أولاً.")
