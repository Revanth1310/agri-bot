from gtts import gTTS
import uuid
import os
import streamlit as st

def generate_audio(text, lang_code='en'):
    filename = f"audio/{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang_code)
    tts.save(filename)
        
    st.audio(filename, autoplay=True)
    return filename
