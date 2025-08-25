"""
app.py

Streamlit app that ties everything together.
"""

import streamlit as st
from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
from security import sanitize_user_text, check_token
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Trip Safety AI", layout="centered")

st.title("Trip Safety AI — Multi-Agent System")
st.caption("Risk Assessment, Advisory & Emergency agents (Demo)")

# Simple auth token (demo)
token = st.sidebar.text_input("Admin token (demo)", type="password")
if not check_token(token):
    st.sidebar.warning("Enter valid admin token to unlock full features (demo).")

st.write("Enter trip details (example: 'I'm traveling from Colombo to Kandy by bus tonight at 9pm')")

user_input = st.text_area("Trip description", value="", height=120)
submit = st.button("Assess Trip")

if submit:
    user_input = sanitize_user_text(user_input)
    if not user_input.strip():
        st.error("Please enter a trip description.")
    else:
        st.info("Running risk assessment...")
        risk_agent = RiskAssessmentAgent()
        assessment = risk_agent.handle(user_input)
        st.subheader("Risk Assessment (structured)")
        st.json(assessment)

        # Advisory
        st.subheader("Advisory")
        advisory_agent = AdvisoryAgent()
        advice = advisory_agent.handle(assessment)
        st.markdown("**Advice:**")
        st.text(advice["advice_text"])

        # Emergency
        st.subheader("Emergency Plan")
        emergency_agent = EmergencyAgent()
        emergency_plan = emergency_agent.handle(assessment)
        st.json(emergency_plan)
        st.success("Done — save results for the report & demo.")
