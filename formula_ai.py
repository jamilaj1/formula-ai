import streamlit as st
import google.generativeai as genai

# --- 1. Global Authentication System ---
USERS = {"admin": "123", "jamil": "123"}

def check_password():
    if "auth" not in st.session_state: 
        st.session_state.auth = False
        
    if not st.session_state.auth:
        st.title("🌐 Formula AI Global")
        st.markdown("Please log in to access the intelligent formulation agent.")
        
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("❌ Invalid credentials. Please try again.")
        return False
    return True

if check_password():
    # --- 2. Global Agent Setup ---
    st.set_page_config(page_title="Formula AI Global", page_icon="🧪")
    
    # Secure API Key retrieval from Streamlit Secrets
    MY_API_KEY = st.secrets["API_KEY"]
    
    @st.cache_resource
    def init_ai(key):
        genai.configure(api_key=key)
        instr = """
        You are 'Formula AI', a world-class expert in Applied Chemistry. 
        Detect the user's language automatically and reply in that exact language. 
        CRITICAL: Keep all technical data, chemical names, formulas, and tables strictly in Professional English. 
        Always ask for: 1) Industry Sector, 2) Formulation Objective, and 3) Mode (A-F) before providing any formulas.
        """
        m_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(model_name=m_list[0], system_instruction=instr)

    try:
        ai_model = init_ai(MY_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize AI: {e}")
    
    # --- 3. Chat Interface ---
    st.title("🧪 Formula AI Agent")
    
    if "msg" not in st.session_state: 
        st.session_state.msg = []
    if "chat" not in st.session_state: 
        st.session_state.chat = ai_model.start_chat(history=[])

    # Display chat history
    for m in st.session_state.msg:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # User input
    if prompt := st.chat_input("Ask in any language..."):
        st.session_state.msg.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                res = st.session_state.chat.send_message(prompt)
                st.markdown(res.text)
                st.session_state.msg.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"API Error: {e}. Please check your API key and connection.")

    # --- 4. Sidebar Controls ---
    with st.sidebar:
        st.header("Control Panel")
        st.markdown("---")
        if st.button("New Session 🧹", use_container_width=True):
            st.session_state.msg = []
            st.session_state.chat = ai_model.start_chat(history=[])
            st.rerun()
