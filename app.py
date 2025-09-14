import streamlit as st
import requests
import json
import os
from utils import advisor

st.title("🍺 AI Responsible Drinking Advisor")

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
            {"role": "system", "content": "You are a responsible drinking AI advisor. Provide safe, clear, and empathetic advice based on user BAC and context."},
            {"role": "user", "content": prompt}
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


# --- Generate Automated LLM Advice ---
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
Based on this drinking session summary, provide safe and responsible advice.

Session details:
{session_summary}
"""

llm_advice = get_llm_response(llm_advice_prompt)

# --- Main Content ---
st.metric("Estimated BAC (%)", f"{bac:.3f}")
st.metric("Risk Level", risk.capitalize())

st.write("### 🤖 AI-Generated Advice")
st.info(llm_advice)

# --- Sidebar: Interactive AI Advisor ---
st.sidebar.markdown("### Chat with AI Advisor")
user_question = st.sidebar.text_area("Ask a question about your drinking session:")
if st.sidebar.button("Get Advisor Response"):
    if user_question.strip():
        full_prompt = f"""
        Session summary:
        {session_summary}

        Question:
        {user_question}
        """
        ai_response = get_llm_response(full_prompt)
        st.sidebar.markdown("### 🔎 Advisor Response")
        st.sidebar.write(ai_response)
    else:
        st.sidebar.warning("Please enter a question before clicking.")
