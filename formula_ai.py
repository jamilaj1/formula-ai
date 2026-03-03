import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. إعدادات الصفحة (Page Configuration) ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# كود CSS لإجبار ظهور العناصر وتنسيقها
st.markdown("""
<style>
    .stApp { background-color: #131314 !important; color: #e3e3e3 !important; }
    /* تنسيق صندوق البحث ليكون في الأسفل وواضحاً */
    .stChatInputContainer {
        padding-bottom: 20px !important;
        background-color: transparent !important;
    }
    .gemini-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ربط قاعدة البيانات والجلسة ---
@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_db()
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### ⚙️ Workspace Settings")
    st.toggle("Dark Mode ✨", value=True, key="theme_toggle")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        st.markdown(f"**Operator:**\n### Jamil Abduljalil")
        if st.button("Logout 🚪", key="logout_btn"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Formulas")
        if st.button("Unlock Pro 🔓", key="unlock_btn"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. واجهة التطبيق الرئيسية (Main Laboratory) ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("How can I help you today?")

    # التحقق من الصلاحية (2 مجانية للضيوف)
    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to unlock unlimited formulas.")
        return

    # تشغيل محرك الذكاء الاصطناعي (Correct Model: gemini-1.5-flash)
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # حل مشكلة 404: استخدام الاسم الصحيح للموديل
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        # عرض المحادثات السابقة
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # --- مكان البحث (The Chat Input) ---
        if prompt := st.chat_input("Ask for a formula or batch requirements...", key="chat_input_main"):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                # نظام هندسي للرد
                response = st.session_state.chat.send_message(f"As an expert engineer, answer: {prompt}")
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
                
    except Exception as e:
        st.error(f"AI System Error: {e}")

# --- 5. نظام التوجيه (Routing) ---
if not is_pro and st.session_state.get('show_auth', False):
    # واجهة التسجيل (تبسيطاً وضعتها هنا)
    st.markdown("### Please Login or Register")
    if st.button("← Back to Lab"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
