import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. إعدادات الصفحة والواجهة (The Ultimate Theme Fix) ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# كود CSS لإجبار الوضع الداكن ومنع أي بقع بيضاء
st.markdown("""
<style>
    /* فرض الخلفية الداكنة على كل التطبيق */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    
    /* تنسيق القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* تنسيق العنوان الرئيسي المتدرج */
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    /* تنسيق صندوق الدردشة */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border-radius: 28px !important;
        border: 1px solid #444746 !important;
    }
    
    /* إخفاء الهيدر الافتراضي */
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. إعداد قاعدة البيانات والجلسة ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. القائمة الجانبية (Personalized Sidebar) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    # زر تبديل الوضع (يعمل برمجياً)
    is_dark = st.toggle("Dark Mode ✨", value=True, key="unique_theme_toggle_id")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            # جلب اسمك "جميل عبد الجليل"
            full_name = user_data.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except:
            full_name = "Jamil Abduljalil"
            
        st.markdown(f"**Operator:**\n### {full_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="unique_logout_button_id"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Formulas")
        if st.button("Unlock Full Access 🔓", key="unique_unlock_button_id"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. واجهة تسجيل الدخول (Fixed Duplicate IDs) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        e_in = st.text_input("Professional Email", key="login_email_unique")
        p_in = st.text_input("Password", type="password", key="login_pass_unique")
        if st.button("Authenticate & Enter", key="login_btn_unique"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_in, "password": p_in})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        n_in = st.text_input("Full Name", placeholder="e.g. Jamil Abduljalil", key="reg_name_unique")
        e_s = st.text_input("Email", key="reg_email_unique")
        p_s = st.text_input("Password (6+ characters)", type="password", key="reg_pass_unique")
        if st.button("Initialize Pro Account", key="reg_btn_unique"):
            try:
                res = supabase.auth.sign_up({
                    "email": e_s, 
                    "password": p_s, 
                    "options": {"data": {"full_name": n_in}}
                })
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- 5. واجهة المختبر الرئيسية (Fixed AI Model) ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to unlock unlimited formulas.")
        return

    # تشغيل محرك الذكاء الاصطناعي
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # التصحيح: استخدام اسم الموديل المستقر
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        # عرض الرسائل السابقة
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter formula query or batch requirements..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # إرسال الرسالة للموديل
                    response = st.session_state.chat.send_message(f"As a Senior Chemical Engineer, answer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_err:
                    st.error(f"AI Engine Error: {ai_err}")
    except Exception as e:
        st.error(f"System Configuration Error: {e}")

# --- 6. التوجيه (Routing) ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Laboratory", key="unique_back_button_id"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
