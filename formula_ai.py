import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import uuid

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# فرض التصميم الاحترافي الداكن لحل مشاكل البقع البيضاء
st.markdown("""
<style>
    .stApp { background-color: #131314 !important; color: #e3e3e3 !important; }
    section[data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid rgba(255,255,255,0.05); }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #444746 !important; border-radius: 28px !important; }
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. تهيئة الاتصال والذكاء الاصطناعي ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_connections():
    # ربط Supabase باستخدام Secrets
    sb_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    # ربط Gemini
    genai.configure(api_key=st.secrets["API_KEY"])
    return sb_client

supabase = init_connections()

# --- 3. نظام المصادقة (حل أخطاء الدخول وتكرار المعرفات) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        # استخدام مفاتيح فريدة لمنع انهيار التطبيق
        e_log = st.text_input("Email", key="unique_login_e")
        p_log = st.text_input("Password", type="password", key="unique_login_p")
        if st.button("Authenticate & Enter", key="unique_login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("❌ Authentication failed.")

    with tab2:
        e_reg = st.text_input("Email", key="unique_reg_e")
        p_reg = st.text_input("Password", type="password", key="unique_reg_p")
        if st.button("Initialize Pro Account", key="unique_reg_btn"):
            try:
                supabase.auth.sign_up({"email": e_reg, "password": p_reg})
                # إضافة السجل للجدول الذي أنشأته بنجاح
                supabase.table("users_usage").insert({"email": e_reg, "is_pro": True}).execute()
                st.success("✅ Account created! Please login.")
            except Exception as e: st.error(f"❌ Error: {e}")

# --- 4. المختبر الرئيسي (حل خطأ 404 القاتل) ---
def render_main():
    with st.sidebar:
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="sidebar_logout_unique"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown('<p class="gemini-title">Formula AI Pro</p>', unsafe_allow_html=True)

    # الحل البرمجي لخطأ 404: نترك المكتبة تختار المسار المستقر تلقائياً
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # تم تثبيت المعرف المستقر
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Enter manufacturing query...", key="global_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # طلب الاستجابة بصفة مهندس كيميائي خبير
                    response = model.generate_content(f"Expert Industrial Engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as ai_err:
                    st.error(f"⚠️ AI Busy. Details: {ai_err}")
    except Exception as e:
        st.error(f"🛑 Critical Model Error: {e}")

# --- 5. نظام التوجيه ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
