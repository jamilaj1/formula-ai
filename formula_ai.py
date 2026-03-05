import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import uuid

# --- 1. إعدادات الصفحة والهوية البصرية ---
# وضع الإعدادات في البداية لتجنب أخطاء التحميل
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# فرض الوضع الداكن الاحترافي لحل مشاكل البقع البيضاء في الصور السابقة
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

# --- 2. تهيئة الاتصال بقاعدة البيانات والذكاء الاصطناعي ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_connections():
    # ربط Supabase باستخدام Secrets لحل أخطاء الربط
    sb_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    
    # ربط Gemini مع اختيار الموديل المستقر لتجنب خطأ 404
    genai.configure(api_key=st.secrets["API_KEY"])
    ai_model = genai.GenerativeModel("gemini-1.5-flash")
    return sb_client, ai_model

supabase, model = init_connections()

# --- 3. نظام المصادقة (حل أخطاء Duplicate ID و Schema Cache) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        # استخدام مفاتيح (keys) فريدة لمنع انهيار التطبيق
        e_log = st.text_input("Professional Email", key="unique_login_email")
        p_log = st.text_input("Password", type="password", key="unique_login_pass")
        if st.button("Authenticate & Enter", key="unique_login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception:
                st.error("❌ Authentication failed. Verify credentials.")

    with tab2:
        n_reg = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="unique_reg_name")
        e_reg = st.text_input("Email", key="unique_reg_email")
        p_reg = st.text_input("Security Password", type="password", key="unique_reg_pass")
        if st.button("Initialize Pro Account", key="unique_reg_btn"):
            try:
                # محاولة التسجيل وإضافة سجل الاستخدام لحل خطأ PGRST205
                auth_res = supabase.auth.sign_up({"email": e_reg, "password": p_reg, "options": {"data": {"full_name": n_reg}}})
                # تأكد من تنفيذ كود SQL الذي شرحته لك سابقاً ليعمل هذا الجزء
                supabase.table("users_usage").insert({"email": e_reg, "is_pro": True}).execute()
                st.success("✅ Account created! Please login.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- 4. المختبر الكيميائي (المساحة الرئيسية) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace Settings")
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="global_logout_unique"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown('<p class="gemini-title">Formula AI Pro</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    # عرض تاريخ المحادثة
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # إدخال الاستفسارات الصناعية
    if prompt := st.chat_input("Enter your manufacturing query...", key="global_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # إرسال الطلب للموديل المستقر
                response = model.generate_content(f"As a Senior Chemical Engineer, answer: {prompt}")
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ AI Core Busy: {e}")

# --- 5. نظام التوجيه (Routing) ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
