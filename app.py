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
    st.error("TensorFlow missing! Please add 'tensorflow-cpu' to requirements.txt")

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="LexGuard AI | منصة التدقيق القانوني",
    page_icon="⚖️",
    layout="wide"
)

# تصميم الواجهة (أسود وذهبي فخم)
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
# ملاحظة: يفضل دائماً استخدام st.secrets["GEMINI_API_KEY"] للأمان
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI" 
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. تحميل موديل الشبكة العصبية (NN) ---
@st.cache_resource
def load_nn_model():
    model_path = 'best_model.h5'
    if os.path.exists(model_path):
        try:
            # تحميل الموديل (بدون الـ optimizer لتقليل مشاكل التوافق)
            model = tf.keras.models.load_model(model_path, compile=False)
            return model
        except Exception as e:
            st.error(f"⚠️ خطأ في قراءة ملف الموديل: {e}")
            return None
    else:
        st.info("ℹ️ لم يتم العثور على ملف 'best_model.h5' محلياً. سيتم الاعتماد على تحليل جيميناي فقط.")
        return None

nn_model = load_nn_model()

# --- 4. وظائف استخراج وتحليل البيانات ---
def scrape_policy(url):
    """سحب وتنظيف نص سياسة الخصوصية"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # حذف العناصر غير الضرورية
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
            
        text = ' '.join(soup.get_text().split())
        return text[:5000] # نأخذ قدراً كافياً للتحليل
    except Exception as e:
        st.error(f"❌ فشل سحب البيانات: {e}")
        return None

def get_gemini_analysis(policy_text, region_law):
    """إرسال النص لجيميناي للتحليل القانوني"""
    prompt = f"""
    أنت مستشار قانوني رقمي متخصص في {region_law}. 
    قم بمراجعة سياسة الخصوصية التالية بدقة:
    
    {policy_text}
    
    المطلوب (باللغة العربية):
    1. قائمة بالمخالفات الصريحة لمواد القانون.
    2. شرح مبسط للمواطن: ماذا يحدث لبياناتك الشخصية عند الموافقة؟
    3. تقييم نهائي لمستوى الأمان والامتثال من 10.
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ في الاتصال بجيميناي: {e}"

# --- 5. واجهة التطبيق الرئيسية ---
st.markdown("<h1 style='text-align: center;'>⚖️ LexGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>نظام هجين للتدقيق القانوني الذكي (Neural Networks + LLMs)</p>", unsafe_allow_html=True)
st.divider()

url_input = st.text_input("📍 أدخل رابط (URL) سياسة الخصوصية للفحص:", placeholder="https://example.com/privacy")

if st.button("🚀 ابدأ الفحص القانوني الشامل"):
    if url_input:
        with st.spinner("جاري سحب النص وتحليله قانونياً..."):
            # الخطوة 1: السحب
            policy_content = scrape_policy(url_input)
            
            if policy_content:
                # الخطوة 2: التحليل عبر جيميناي
                report_egypt = get_gemini_analysis(policy_content, "قانون حماية البيانات الشخصية المصري (151 لعام 2020)")
                report_gdpr = get_gemini_analysis(policy_content, "اللائحة العامة لحماية البيانات الأوروبية (GDPR)")
                
                # عرض النتائج في أعمدة
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.subheader("🇪🇬 معايير القانون المصري")
                    st.write(report_egypt)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown('<div class="report-card">', unsafe_allow_html=True)
                    st.subheader("🇪🇺 معايير الـ GDPR")
                    st.write(report_gdpr)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.success("✅ تم الانتهاء من عملية التدقيق القانوني.")
            else:
                st.error("تعذر قراءة محتوى الرابط. تأكد من صحته.")
    else:
        st.warning("يرجى إدخال الرابط أولاً.")

# Footer
st.markdown("<br><hr><p style='text-align: center; color: #555;'>LexGuard AI - Powered by Gemini & TensorFlow</p>", unsafe_allow_html=True)
