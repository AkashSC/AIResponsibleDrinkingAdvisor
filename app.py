import streamlit as st
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

# Calculate
grams = advisor.grams_of_alcohol(volume_ml, abv)
bac = advisor.estimate_bac_percent(grams, weight, gender, hours)
risk = advisor.classify_risk(bac)
advice = advisor.advice_bundle(bac, 1, asked_to_drive)

st.metric("Estimated BAC (%)", f"{bac:.3f}")
st.metric("Risk Level", risk.capitalize())
st.write("### Advice")
st.info(advice)

# Visualizations
st.write("### BAC Series (Sample Session)")
visualizer.plot_bac_series(bac_series)

st.write("### Risk Distribution (Sample Events)")
visualizer.plot_risk_distribution(events)
