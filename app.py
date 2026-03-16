import streamlit as st
import google.generativeai as genai
import tensorflow as tf
import requests
from bs4 import BeautifulSoup
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="LexGuard AI | خبير الامتثال", layout="wide", page_icon="⚖️")

# ستايل احترافي (ذهبي في أسود) ليعطي طابع الفخامة القانونية
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #daa520; }
    .stButton>button { background-color: #b8860b; color: white; width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .stButton>button:hover { background-color: #daa520; color: black; }
    .report-box { background-color: #1a1c24; padding: 20px; border-radius: 10px; border-left: 5px solid #daa520; margin-bottom: 20px; }
    h1, h2, h3 { color: #daa520 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNECT TO GEMINI ---
# المفتاح الذي أرسلتيه
API_KEY = "AIzaSyC94B8M4NCTG58iQGDs4Ei0R7RsBNHUDJI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. FUNCTIONS ---
def scrape_policy(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for s in soup(['script', 'style']): s.decompose()
        text = ' '.join(soup.get_text().split())
        return text[:4000] # نأخذ جزء كافي للتحليل
    except:
        return None

# --- 4. MAIN INTERFACE ---
st.markdown("<h1>⚖️ منصة LexGuard AI للتدقيق القانوني</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>فحص ذكي لسياسات الخصوصية بناءً على التشريعات المصرية والأوروبية</p>", unsafe_allow_html=True)

url_input = st.text_input("ضع رابط سياسة الخصوصية هنا (URL):", placeholder="https://example.com/privacy")

if st.button("إجراء تحليل امتثال عميق"):
    if url_input:
        with st.status("🛠️ جاري تشغيل المحلل الذكي...", expanded=True) as status:
            # Step 1: Scraping
            st.write("📡 جاري سحب بيانات السياسة من الموقع...")
            policy_text = scrape_policy(url_input)
            
            if policy_text:
                st.write("🧠 جاري الربط مع Gemini للتحليل القانوني...")
                
                # التحليل المزدوج (مصر وأوروبا)
                def get_legal_report(region):
                    prompt = f"""
                    أنت مستشار قانوني رقمي خبير في {region}.
                    حلل سياسة الخصوصية التالية: {policy_text}
                    
                    المطلوب منك باللغة العربية:
                    1. تحديد المخالفات الصريحة لهذا القانون.
                    2. شرح المخاطر على بيانات المواطن العادي بأسلوب مبسط.
                    3. تقييم نهائي للامتثال من 10.
                    """
                    return gemini_model.generate_content(prompt).text

                eg_report = get_legal_report("قانون حماية البيانات الشخصية المصري 151 لسنة 2020")
                eu_report = get_legal_report("اللائحة العامة لحماية البيانات الأوروبية (GDPR)")

                status.update(label="✅ تم التحليل بنجاح!", state="complete", expanded=False)

                # --- عرض النتائج ---
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.header("🇪🇬 القانون المصري")
                    st.write(eg_report)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.header("🇪🇺 القانون الأوروبي (GDPR)")
                    st.write(eu_report)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("فشلنا في الوصول لرابط الموقع، تأكد من صحته.")
    else:
        st.warning("يرجى إدخال الرابط أولاً.")
