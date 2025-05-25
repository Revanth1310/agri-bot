import streamlit as st
from fetch_sites import fetch_content_from_sites
from gemini_api import query_gemini
from tts import generate_audio
from utils import get_coords_from_browser, get_environment_data
import time
from datetime import datetime
import os

st.set_page_config(page_title="🌿 Agri Assistant", layout="wide")

# ----- Initialize Session State -----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_store" not in st.session_state:
    st.session_state.conversation_store = {}
if "selected_convo" not in st.session_state:
    st.session_state.selected_convo = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "live"
if "language" not in st.session_state:
    st.session_state.language = "en"
if "location_loaded" not in st.session_state:
    st.session_state.location_loaded = False
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "input_submitted" not in st.session_state:
    st.session_state.input_submitted = False

# ----- Load Saved History -----
if os.path.exists("history_log.txt") and not st.session_state.conversation_store:
    with open("history_log.txt", "r", encoding="utf-8") as log:
        current_title = None
        history = []
        for line in log:
            line = line.strip()
            if line.startswith("[Chat"):
                if current_title and history:
                    st.session_state.conversation_store[current_title] = {
                        "history": history,
                        "meta": {"lat": "", "lon": "", "env": {}, "timestamp": ""}
                    }
                current_title = line.strip("[]")
                history = []
            elif line.startswith("Q:"):
                q = line[2:].strip()
            elif line.startswith("A:"):
                a = line[2:].strip()
                history.append((q, a))
        if current_title and history:
            st.session_state.conversation_store[current_title] = {
                "history": history,
                "meta": {"lat": "", "lon": "", "env": {}, "timestamp": ""}
            }

# ----- Top Title -----
st.markdown("<h1 style='text-align: center;'>🌿 Agricultural Assistant Bot</h1>", unsafe_allow_html=True)

# ----- Get Location and Environment Data -----
lat, lon = get_coords_from_browser()
try:
    lat = float(lat)
    lon = float(lon)
    env_data = get_environment_data(lat, lon)
except:
    lat, lon = None, None
    env_data = {"temperature": "N/A", "soil_moisture": "N/A", "air_quality": "N/A"}

# ----- Layout: 3 Panels -----
left, center, right = st.columns([1.2, 3, 1.2])

# ===== LEFT PANE =====
with left:
    st.markdown("### 🌐 Language")
    language_selection = st.selectbox("Select Language", ["English", "Hindi", "Tamil", "Telugu", "Marathi"])
    st.session_state.language = language_selection

    st.markdown("---")
    st.markdown("### 📜 History")
    if st.button("➕ New Chat"):
        st.session_state.chat_history = []
        st.session_state.view_mode = "live"
        st.session_state.selected_convo = None
    for title in st.session_state.conversation_store:
        if st.button(title):
            st.session_state.view_mode = "history"
            st.session_state.selected_convo = title

    

# ===== RIGHT PANE =====
with right:
    st.markdown("### 🌦️ Environment")
    if lat and lon:
        st.markdown(f"**📍 Location:** {lat}, {lon}")
        st.markdown(f"**🌡️ Temperature:** {env_data['temperature']} °C")
        st.markdown(f"**💧 Soil Moisture:** {env_data['soil_moisture']}")
        st.markdown(f"**🌫️ Air Quality:** {env_data['air_quality']}")
    else:
        st.warning("Waiting for location...")

# ===== CENTER PANE =====
with center:
    st.markdown("### 💬 Conversation")

    user_query = st.chat_input("Type your question ➔")

    if user_query is not None and user_query.strip() != "" and not st.session_state.input_submitted:
        st.session_state.input_submitted = True
        context = fetch_content_from_sites(user_query)
        history_txt = "\n".join([f"User: {q}\nAI: {a}" for q, a in st.session_state.chat_history])
        env_summary = f"Temp: {env_data['temperature']} °C, Soil: {env_data['soil_moisture']}, Air: {env_data['air_quality']}"
        

        

        prompt = f"""
        You are an AI assistant for Indian farmers.

        Location: {lat}, {lon}
        Environment: {env_summary}

        Previous conversation:
        {history_txt}

        Current question:
        {user_query}

        Relevant government agriculture portal data:
        {context}

        Respond helpfully in {language_selection}. Use simple and clear language suited for farmers.
        """

        st.markdown(f"**You:** {user_query}")
        placeholder = st.empty()
        response = query_gemini(prompt)
        final = ""
        for word in response.split():
            final += word + " "
            placeholder.markdown(f"**Bot:** {final}")
            time.sleep(0.04)
        st.session_state.chat_history.append((user_query, response))
        st.session_state.last_response = response
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        st.session_state.conversation_store[title] = {
            "history": st.session_state.chat_history.copy(),
            "meta": {
                "lat": lat, "lon": lon,
                "env": env_data,
                "timestamp": datetime.now().isoformat()
            }
        }
        with open("history_log.txt", "a", encoding="utf-8") as log:
            log.write(f"\n[{title}]\n")
            for q, a in st.session_state.chat_history:
                log.write(f"Q: {q}\nA: {a}\n")
        st.rerun()

    current_chat = st.session_state.chat_history if st.session_state.view_mode == "live" \
                   else st.session_state.conversation_store.get(
                       st.session_state.selected_convo, {}).get("history", [])

    for q, a in current_chat:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Bot:** {a}")
        if a == st.session_state.last_response:
            TTS_LANG_MAP = {
                "en": "en",
                "hi": "hi",
                "ta": "ta",
                "te": "te",
                "mr": "mr"
            }
            lang_code = TTS_LANG_MAP.get(st.session_state.language, "en")
            if st.button("🔊 Play Response", key=f"play_{q}"):
                audio_file = generate_audio(a, lang_code)
                st.audio(audio_file)

if user_query is None or user_query.strip() == "":
    st.session_state.input_submitted = False
