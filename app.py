import streamlit as st
import requests
import json
import os
import base64
from gtts import gTTS

st.title("🍺 AI Responsible Drinking Advisor")

# -----------------------------
# Core Functions
# -----------------------------
def grams_of_alcohol(volume_ml, abv):
    return volume_ml * (abv / 100) * 0.789  # 0.789 g/ml is ethanol density

def estimate_bac_percent(grams, weight, gender, hours):
    r = 0.68 if gender == "M" else 0.55
    bac = (grams / (weight * r)) * 100
    bac = bac - (0.015 * hours)  # natural elimination rate
    return max(bac, 0)

def classify_risk(bac):
    if bac < 0.03:
        return "low"
    elif bac < 0.08:
        return "moderate"
    else:
        return "high"

# -----------------------------
# LLM Response Function (Groq)
# -----------------------------
def get_llm_response(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY environment variable not set in Render."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a responsible drinking AI advisor. Provide short, safe, empathetic advice (2–3 sentences)."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 120
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return f"⚠️ API Error: {response.text}"
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Unexpected Error: {e}"

# -----------------------------
# Text-to-Speech (TTS)
# -----------------------------
def text_to_speech(text: str):
    tts = gTTS(text)
    tts.save("advice.mp3")
    with open("advice.mp3", "rb") as f:
        b64_audio = base64.b64encode(f.read()).decode()
    audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# -----------------------------
# Sidebar Input
# -----------------------------
st.sidebar.header("User Input")
volume_ml = st.sidebar.number_input("Drink volume (ml)", min_value=0, value=330)
abv = st.sidebar.slider("Alcohol % (ABV)", 0.0, 50.0, 5.0)
weight = st.sidebar.number_input("Body weight (kg)", min_value=40, max_value=150, value=70)
gender = st.sidebar.selectbox("Gender", ["M", "F"])
hours = st.sidebar.slider("Hours since drinking started", 0.0, 12.0, 1.0)
asked_to_drive = st.sidebar.checkbox("Asked to drive?")

# -----------------------------
# Calculations
# -----------------------------
grams = grams_of_alcohol(volume_ml, abv)
bac = estimate_bac_percent(grams, weight, gender, hours)
risk = classify_risk(bac)

# -----------------------------
# AI Advice (auto-updates with inputs)
# -----------------------------
session_summary = f"""
Drink Volume: {volume_ml} ml
ABV: {abv}%
Weight: {weight} kg
Gender: {gender}
Hours since drinking started: {hours}
Estimated BAC: {bac:.3f}%
Risk Level: {risk}
Asked to drive: {asked_to_drive}
"""

llm_advice_prompt = f"""
Based on this drinking session summary, give short and clear advice (2–3 sentences max).

Session details:
{session_summary}
"""

llm_advice = get_llm_response(llm_advice_prompt)

# -----------------------------
# Display
# -----------------------------
st.metric("Estimated BAC (%)", f"{bac:.3f}")
st.metric("Risk Level", risk.capitalize())

col1, col2 = st.columns([4,1])
with col1:
    st.subheader("🤖 AI-Generated Advice")
with col2:
    if st.button("🔊 Read Out"):
        text_to_speech(llm_advice)

st.info(llm_advice)
