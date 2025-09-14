import streamlit as st
import requests, os, random
from gtts import gTTS
import base64

# -----------------------------
# Text-to-Speech
# -----------------------------
def text_to_speech(text: str):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("advice.mp3")
        with open("advice.mp3", "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
            <audio autoplay controls>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Text-to-Speech Error: {e}")

# -----------------------------
# LLM Response Function (Groq)
# -----------------------------
def get_llm_response(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY environment variable not set."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful AI responsible drinking advisor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
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
# BAC Calculation
# -----------------------------
def grams_of_alcohol(volume_ml, abv):
    return volume_ml * (abv / 100) * 0.789

def estimate_bac_percent(grams, weight, gender, hours):
    r = 0.68 if gender == "M" else 0.55
    bac = (grams / (weight * r)) * 100 - (0.015 * hours)
    return max(bac, 0)

def classify_risk(bac):
    if bac == 0:
        return "Sober"
    elif bac < 0.03:
        return "Low"
    elif bac < 0.08:
        return "Moderate"
    elif bac < 0.20:
        return "High"
    else:
        return "Very High"

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🍺 AI Responsible Drinking Advisor")

# Sidebar Input
st.sidebar.header("User Input")
volume_ml = st.sidebar.number_input("Drink volume (ml)", min_value=0, value=330)
abv = st.sidebar.slider("Alcohol % (ABV)", 0.0, 50.0, 5.0)
weight = st.sidebar.number_input("Body weight (kg)", min_value=40, max_value=150, value=70)
gender = st.sidebar.selectbox("Gender", ["M", "F"])
hours = st.sidebar.slider("Hours since drinking started", 0.0, 12.0, 1.0)

# Calculate BAC & Risk
grams = grams_of_alcohol(volume_ml, abv)
bac = estimate_bac_percent(grams, weight, gender, hours)
risk = classify_risk(bac)

# -----------------------------
# Generate advice dynamically when inputs change
# -----------------------------
# Create a key representing current input state
input_key = f"{volume_ml}_{abv}_{weight}_{gender}_{hours}"

if "advice_key" not in st.session_state or st.session_state.advice_key != input_key:
    prompt = f"""
    My BAC is estimated at {bac:.3f}%. 
    I am a {weight}kg {gender} who drank {volume_ml}ml at {abv}% ABV over {hours} hours.
    Provide short, friendly advice on responsible drinking including driving safety.
    Keep the advice strictly 8-10 lines.
    """
    llm_advice = get_llm_response(prompt)
    responsible_tips = [
        "Stay hydrated — drink water between drinks.",
        "Eat before and while drinking.",
        "Never drink and drive; arrange safe transport.",
        "Pace yourself — one drink per hour.",
        "Track your intake to stay aware."
    ]
    extra_tip = random.choice(responsible_tips)
    combined_advice = f"{llm_advice}\n\n---\n✅ Tip: {extra_tip}"

    st.session_state.llm_advice = combined_advice
    st.session_state.advice_key = input_key

# Display Results
st.metric("Estimated BAC (%)", f"{bac:.3f}")
st.metric("Risk Level", risk)

col1, col2 = st.columns([1,1])
with col1:
    st.subheader("AI-Generated Advice")
with col2:
    if st.button("🔊 Read Out"):
        text_to_speech(st.session_state.llm_advice)

st.info(st.session_state.llm_advice)
