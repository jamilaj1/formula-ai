import streamlit as st
import google.generativeai as genai

# --- 1. Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(page_title="Formula AI Global", page_icon="🌍")

# --- 2. User Authentication System ---
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
        
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if user in USERS and USERS[user] == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if check_password():
    # --- 3. Sidebar Configuration ---
    with st.sidebar:
        st.title("🌍 Global Control")
        if st.button("New Session 🧹", use_container_width=True):
            # Clear both visual messages and the internal Gemini memory
            st.session_state.messages = []
            if "chat_session" in st.session_state:
                del st.session_state.chat_session
            st.rerun()
            
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # --- 4. AI Initialization (Multilingual) ---
    # WARNING: Replace with your NEW API key. Never share it publicly.
    MY_API_KEY = "YOUR_NEW_API_KEY_HERE" 
    
    @st.cache_resource
    def load_global_model(api_key):
        genai.configure(api_key=api_key)
        
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
        # Explicitly selecting a highly capable model for text/chat
        return genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=global_instructions
        )

    try:
        model = load_global_model(MY_API_KEY)
    except Exception as e:
        st.error(f"Configuration Error: Please check your API key. Details: {e}")
        st.stop()

    # --- 5. Chat Interface ---
    st.title("🧪 Formula AI Global Agent")
    st.info("I support all languages. Start by describing your project.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input and execution
    if prompt := st.chat_input("Ask your chemical formulation question here..."):
        # Append and display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing formulation parameters..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"API Error: Unable to generate response. {e}")
