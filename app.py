import streamlit as st
import requests
import json
import os
from utils import data_loader, advisor, visualizer

st.title("🍺 AI Responsible Drinking Advisor")

# Load datasets
events, sessions, users, bac_series = data_loader.load_all()

# Sidebar input
st.sidebar.header("User Input")
volume_ml = st.sidebar.number_input("Drink volume (ml)", min_value=0, value=330)
abv = st.sidebar.slider("Alcohol % (ABV)", 0.0, 50.0, 5.0)
weight = st.sidebar.number_input("Body weight (kg)", min_value=40, max_value=150, value=70)
gender = st.sidebar.selectbox("Gender", ["M", "F"])
hours = st.sidebar.slider("Hours since drinking started", 0.0, 12.0, 1.0)
asked_to_drive = st.sidebar.checkbox("Asked to drive?")

# --- Core Calculations ---
grams = advisor.grams_of_alcohol(volume_ml, abv)
bac = advisor.estimate_bac_percent(grams, weight, gender, hours)
risk = advisor.classify_risk(bac)
advice = advisor.advice_bundle(bac, 1, asked_to_drive)

# -----------------------------
# LLM Response Function (Groq)
# -----------------------------
def get_llm_response(prompt: str, data_summary: str = "") -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY environment variable not set in Render."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    clean_prompt = prompt.strip()
    if not clean_prompt:
        return "⚠️ Please enter a valid question."

    # Combine query + dataset context
    full_prompt = f"""
    You are an AI responsible drinking advisor.
    Use the BAC calculation and user details below to answer clearly and responsibly.

    Session summary:
    - Drink Volume: {volume_ml} ml
    - ABV: {abv}%
    - Weight: {weight} kg
    - Gender: {gender}
    - Hours since drinking started: {hours}
    - Estimated BAC: {bac:.3f}%
    - Risk Level: {risk}
    - Asked to drive: {asked_to_drive}

    Question:
    {clean_prompt}
    """

    payload = {
        "model": "llama-3.1-8b-instant",  # ✅ supported Groq model
        "messages": [
            {"role": "system", "content": "You are a helpful AI advisor for responsible drinking."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            try:
                err_data = response.json()
                return f"⚠️ API Error:\n```json\n{json.dumps(err_data, indent=2)}\n```"
            except Exception:
                return f"⚠️ HTTP {response.status_code}: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Unexpected Error: {e}"

# --- AI Advisor input ---
st.sidebar.markdown("### 🤖 AI Advisor")
user_question = st.sidebar.text_area("Ask your AI Advisor:")
if st.sidebar.button("Get Advice"):
    if user_question.strip():
        data_summary = f"BAC={bac:.3f}, Risk={risk}, Weight={weight}, Gender={gender}, Hours={hours}"
        ai_response = get_llm_response(user_question, data_summary)
        st.sidebar.success(ai_response)
    else:
        st.sidebar.warning("Please enter a question before clicking Get Advisor.")

# --- Display core results ---
st.metric("Estimated BAC (%)", f"{bac:.3f}")
st.metric("Risk Level", risk.capitalize())
st.write("### Advice")
st.info(advice)

# --- Visualizations ---
st.write("### BAC Series (Sample Session)")
visualizer.plot_bac_series(bac_series)

st.write("### Risk Distribution (Sample Events)")
visualizer.plot_risk_distribution(events)
