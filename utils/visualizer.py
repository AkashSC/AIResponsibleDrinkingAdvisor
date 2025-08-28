import plotly.express as px
import streamlit as st

def plot_bac_series(bac_df):
    fig = px.line(
        bac_df,
        x="time",
        y="bac_percent",
        title="Blood Alcohol Concentration Over Time",
        labels={"time": "Time (hours)", "bac_percent": "BAC (%)"},
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

def plot_risk_distribution(events):
    fig = px.histogram(
        events,
        x="risk_level",
        title="Distribution of Risk Levels",
        color="risk_level",
    )
    fig.update_layout(template="plotly_white", bargap=0.2)
    st.plotly_chart(fig, use_container_width=True)
