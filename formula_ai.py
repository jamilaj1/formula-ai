import streamlit as st
import google.generativeai as genai

# --- 1. نظام المستخدمين ---
USERS = {
    "admin": "formula2026",
    "jamil": "ghana2026"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🌐 Formula AI Global")
        st.write("Login to access the world's advanced chemical agent.")
        
        user = st.text_input("Username / اسم المستخدم")
        password = st.text_input("Password / كلمة المرور", type="password")
        
        if st.button("Login / دخول"):
            if user in USERS and USERS[user] == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect credentials / بيانات خاطئة")
        return False
    return True

if check_password():
    # --- 2. إعدادات الواجهة العالمية ---
    st.set_page_config(page_title="Formula AI Global", page_icon="🌍")
    
    with st.sidebar:
        st.title("🌍 Global Control")
        if st.button("New Session / جلسة جديدة 🧹", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("Logout / خروج 🚪"):
            st.session_state.authenticated = False
            st.rerun()

    # --- 3. تهيئة الذكاء الاصطناعي (متعدد اللغات) ---
    MY_API_KEY = st.secrets["API_KEY"]
    
    @st.cache_resource
    def load_global_model(api_key):
        genai.configure(api_key=api_key)
        # تعليمات "العالمية": الوكيل سيتعرف على لغة المستخدم تلقائياً
        global_instructions = """
        You are 'Formula AI', a global expert in Applied Chemistry.
        
        MULTILINGUAL RULES:
        1. Detect the user's language automatically and respond in the SAME language.
        2. TECHNICAL DATA: Always keep chemical names, formulas, and tables in Professional English to ensure global standards.
        3. EXPLANATIONS: Provide instructions and safety notes in the user's native language.
        
        STRICT PROTOCOL:
        - First response must ALWAYS ask for: 1) Industry Sector, 2) Objective, 3) Mode (A-F).
        - Do not provide formulas until these are defined.
        """
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(model_name=models[0], system_instruction=global_instructions)

    model = load_global_model(MY_API_KEY)

    # --- 4. واجهة المحادثة ---
    st.title("🧪 Formula AI Global Agent")
    st.info("I support all languages. Start by describing your project.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask in any language... اسأل بأي لغة"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)

            st.session_state.messages.append({"role": "assistant", "content": response.text})
