"""
Afnan's AI - Futuristic Streamlit Web Neural Assistant.
Sleek cyberpunk dark-mode GUI with GPU/CPU mode toggle and zero hardware clutter.
"""

import streamlit as st
import json
import datetime
from core.client import OllamaClient
from core.personas import PERSONAS, DEFAULT_PERSONA
from core.config import AppConfig
from core.database import DatabaseManager

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Afnan's AI • Autonomous Neural Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Futuristic Cyberpunk / Glassmorphic CSS
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #060810;
        color: #F8FAFC;
        font-family: 'Segoe UI', -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B0E19 0%, #060812 100%);
        border-right: 1px solid #161D33;
    }
    
    /* Futuristic Status Card */
    .status-card {
        background: linear-gradient(135deg, #0F1426 0%, #0A0D1B 100%);
        border: 1px solid #1E2749;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 240, 255, 0.05);
    }
    .status-title {
        font-size: 11px;
        font-weight: 800;
        color: #00F0FF;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .status-badge {
        font-size: 12px;
        font-weight: 700;
        color: #10B981;
        letter-spacing: 0.5px;
    }
    .engine-badge-gpu {
        display: inline-block;
        background-color: rgba(0, 240, 255, 0.12);
        color: #00F0FF;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 12px;
        border: 1px solid rgba(0, 240, 255, 0.3);
        margin-top: 6px;
    }
    .engine-badge-cpu {
        display: inline-block;
        background-color: rgba(167, 139, 250, 0.12);
        color: #C4B5FD;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 12px;
        border: 1px solid rgba(167, 139, 250, 0.3);
        margin-top: 6px;
    }
    
    /* Neon Chat Elements */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 8px;
    }
    
    /* Section Headers */
    .cyber-header {
        font-size: 11px;
        font-weight: 800;
        color: #38BDF8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services & SQLite Database
@st.cache_resource
def get_services():
    config = AppConfig()
    client = OllamaClient(config.ollama_host)
    client.ensure_server_running()
    db = DatabaseManager()
    return config, client, db

config, client, db = get_services()

# Manage Session State
if "current_session_id" not in st.session_state:
    existing_sessions = db.get_sessions()
    if existing_sessions:
        st.session_state.current_session_id = existing_sessions[0]["id"]
    else:
        st.session_state.current_session_id = db.create_session("New Conversation", DEFAULT_PERSONA, config.default_model)

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color: #00F0FF; font-weight: 800; font-size: 24px; letter-spacing: 2px; margin-bottom: 0px;'>✦ AFNAN'S AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #818CF8; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;'>AUTONOMOUS NEURAL ASSISTANT</p>", unsafe_allow_html=True)

    # ➕ New Conversation Button
    if st.button("➕ NEW CONVERSATION", use_container_width=True, type="primary"):
        new_id = db.create_session("New Conversation", DEFAULT_PERSONA, config.default_model)
        st.session_state.current_session_id = new_id
        st.rerun()

    # Saved Conversations from Database
    sessions = db.get_sessions(limit=25)
    session_options = {s["id"]: f"✦ {s['title'][:25]}" for s in sessions}
    
    if st.session_state.current_session_id not in session_options and sessions:
        st.session_state.current_session_id = sessions[0]["id"]

    selected_sid = st.selectbox(
        "// CONVERSATION VAULT",
        options=list(session_options.keys()),
        format_func=lambda sid: session_options.get(sid, sid),
        index=list(session_options.keys()).index(st.session_state.current_session_id) if st.session_state.current_session_id in session_options else 0
    )
    if selected_sid != st.session_state.current_session_id:
        st.session_state.current_session_id = selected_sid
        st.rerun()

    # Compute Engine Selection (GPU vs CPU Mode)
    st.markdown("---")
    saved_mode = db.get_setting("compute_mode", "gpu")
    mode_options = ["🚀 GPU Mode (Hardware Accelerated)", "💻 CPU Mode (Universal / Non-GPU)"]
    mode_default_idx = 1 if saved_mode == "cpu" else 0
    
    compute_selection = st.selectbox(
        "// COMPUTE ENGINE",
        mode_options,
        index=mode_default_idx
    )
    is_cpu_mode = ("CPU" in compute_selection)
    current_mode_str = "cpu" if is_cpu_mode else "gpu"
    if current_mode_str != saved_mode:
        db.set_setting("compute_mode", current_mode_str)

    # Futuristic Status Card (No raw hardware specs)
    if is_cpu_mode:
        st.markdown("""
        <div class="status-card">
            <div class="status-title">SYSTEM CORE</div>
            <div class="status-badge">● NEURAL LINK: ACTIVE</div>
            <div class="engine-badge-cpu">💻 CPU ENGINE (UNIVERSAL)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card">
            <div class="status-title">SYSTEM CORE</div>
            <div class="status-badge">● NEURAL LINK: ACTIVE</div>
            <div class="engine-badge-gpu">⚡ GPU ACCELERATION ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)

    # Assistant Persona
    st.markdown("---")
    st.markdown("<div class='cyber-header'>// NEURAL PERSONA</div>", unsafe_allow_html=True)
    persona_choice = st.selectbox(
        "Select Persona:",
        list(PERSONAS.keys()),
        index=0,
        label_visibility="collapsed"
    )
    st.caption(PERSONAS[persona_choice]["description"])

    # Model Selection
    st.markdown("---")
    st.markdown("<div class='cyber-header'>// ACTIVE MODEL</div>", unsafe_allow_html=True)
    available_models = client.list_models()
    if not available_models:
        available_models = [config.default_model]

    default_idx = 0
    for idx, m in enumerate(available_models):
        if "0.5b" in m or "1b" in m:
            default_idx = idx
            break

    selected_model = st.selectbox(
        "Select Model:",
        available_models,
        index=default_idx,
        label_visibility="collapsed"
    )

    # Generation Parameters
    st.markdown("---")
    st.markdown("<div class='cyber-header'>// PARAMETERS</div>", unsafe_allow_html=True)
    temperature = st.slider("Creativity (Temperature)", 0.1, 1.0, 0.7, 0.05)
    context_size = st.select_slider(
        "Context Window Limit",
        options=[1024, 2048, 4096],
        value=2048
    )

    # Database Actions
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Delete", use_container_width=True):
            db.delete_session(st.session_state.current_session_id)
            st.session_state.current_session_id = None
            st.rerun()
    with col2:
        export_md = db.export_session_markdown(st.session_state.current_session_id)
        st.download_button(
            "💾 Export",
            export_md,
            file_name=f"Afnan_AI_Chat_{st.session_state.current_session_id[:8]}.md",
            mime="text/markdown",
            use_container_width=True
        )

# Main Chat View
st.subheader("💬 Afnan's AI Interface")

# Load Messages for current session from SQLite
db_messages = db.get_messages(st.session_state.current_session_id)

if not db_messages:
    with st.chat_message("assistant"):
        st.markdown(
            "### ✦ Greetings! I am Afnan's AI.\n\n"
            "I am your personal autonomous neural assistant. How can I help you today?\n\n"
            "**Core Capabilities:**\n"
            "- 💡 **Inquiry & Brainstorming:** Instant answers, deep breakdowns, conceptual clarity.\n"
            "- 💻 **Code & Engineering:** Python, C++, ML pipelines, syntax debugging, architecture.\n"
            "- 📝 **Writing & Synthesis:** Technical briefs, executive emails, essay structuring.\n\n"
            "*Choose a neural persona on the left or select a prompt below to begin.*"
        )

    # Starter prompt pills
    st.caption("Prompt Suggestions:")
    prompt_cols = st.columns(3)
    with prompt_cols[0]:
        if st.button("💡 Explain Quantum Computing simply", use_container_width=True):
            st.session_state.temp_input = "Explain Quantum Computing in simple terms using everyday analogies."
    with prompt_cols[1]:
        if st.button("💻 Python script to organize downloads", use_container_width=True):
            st.session_state.temp_input = "Write a clean Python script to organize files in my Downloads folder by extension."
    with prompt_cols[2]:
        if st.button("📝 Draft project update report", use_container_width=True):
            st.session_state.temp_input = "Draft a polite and concise email updating my manager on the machine learning project status."
else:
    # Render saved messages from SQLite
    for msg in db_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User prompt input
initial_prompt = getattr(st.session_state, "temp_input", None)
if initial_prompt:
    del st.session_state.temp_input
    user_query = initial_prompt
else:
    user_query = st.chat_input("Ask Afnan's AI anything...")

if user_query:
    # Save user message to SQLite database
    db.add_message(st.session_state.current_session_id, "user", user_query, model=selected_model)
    
    # Update title if it's the first message of a new session
    session_info = db.get_session(st.session_state.current_session_id)
    if session_info and session_info["title"] == "New Conversation":
        db.update_session_title(st.session_state.current_session_id, user_query.strip()[:26])

    # Display user query
    with st.chat_message("user"):
        st.markdown(user_query)

    # Build messages context with System Prompt
    system_text = PERSONAS.get(persona_choice, {}).get("system_prompt", "")
    api_messages = [{"role": "system", "content": f"You are Afnan's AI. {system_text}"}]
    
    # Include recent chat history from database
    recent_db = db.get_messages(st.session_state.current_session_id)
    for m in recent_db[-7:]:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Determine GPU layers: 0 for CPU mode, 99 for GPU mode
    gpu_layers = 0 if is_cpu_mode else 99

    # Assistant streaming response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_text = ""
        
        for chunk in client.chat_stream(
            messages=api_messages,
            model=selected_model,
            temperature=temperature,
            num_ctx=context_size,
            gpu_layers=gpu_layers
        ):
            full_text += chunk
            response_placeholder.markdown(full_text + "▌")
            
        response_placeholder.markdown(full_text)
        
    # Persist assistant response to SQLite database
    db.add_message(st.session_state.current_session_id, "assistant", full_text, model=selected_model)
    st.rerun()
