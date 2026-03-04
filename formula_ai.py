import streamlit as st
import google.generativeai as genai

# --- 1. نظام الدخول العالمي ---
USERS = {"admin": "123", "jamil": "123"}

def check_password():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("🌐 Formula AI Global")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in USERS and USERS[u] == p:
                st.session_state.auth = True
                st.rerun()
            else: st.error("Wrong Data")
        return False
    return True

if check_password():
    # --- 2. إعدادات الوكيل المتعدد اللغات ---
    st.set_page_config(page_title="Formula AI Global", page_icon="🧪")
    MY_API_KEY = "ضع_مفتاحك_هنا" # ضع مفتاح الـ API الخاص بك هنا
    
    @st.cache_resource
    def init_ai(key):
        genai.configure(api_key=key)
        instr = "You are 'Formula AI'. Detect user language and reply in it. Technical data in English. Ask for Sector, Objective, and Mode (A-F) first."
        # البحث التلقائي عن الموديل المتاح
        m_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(model_name=m_list[0], system_instruction=instr)

    ai_model = init_ai(MY_API_KEY)
    
    # --- 3. واجهة المحادثة ---
    st.title("🧪 Formula AI Agent")
    if "msg" not in st.session_state: st.session_state.msg = []
    if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

    for m in st.session_state.msg:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask in any language..."):
        st.session_state.msg.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = st.session_state.chat.send_message(prompt)
            st.markdown(res.text)
            st.session_state.msg.append({"role": "assistant", "content": res.text})

    if st.sidebar.button("New Session / جلسة جديدة"):
        st.session_state.msg = []
        st.rerun()
