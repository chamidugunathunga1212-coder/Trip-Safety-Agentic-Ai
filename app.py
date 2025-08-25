# """
# app.py

# Streamlit app that ties everything together with improved UI.
# """

# import streamlit as st
# from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
# from security import sanitize_user_text, check_token
# from dotenv import load_dotenv

# load_dotenv()

# # ----------------- Page Config -----------------
# st.set_page_config(
#     page_title="🚦 Trip Safety AI",
#     layout="centered",
#     page_icon="🚌"
# )

# # ----------------- Header -----------------
# st.title("🚦 Trip Safety AI — Multi-Agent System")
# st.caption("🤖 Risk Assessment | 💡 Advisory | 🚑 Emergency Agents (Demo)")

# # ----------------- Sidebar -----------------
# with st.sidebar:
#     st.header("🔑 Authentication")
#     token = st.text_input("Admin token (demo)", type="password")
#     if not check_token(token):
#         st.warning("⚠️ Enter valid admin token to unlock full features.")

#     st.markdown("---")
#     st.info("ℹ️ This is a demo prototype using AI agents for trip safety.")

# # ----------------- Main Input -----------------
# st.markdown("### 📝 Enter Trip Details")
# st.write("Example: *I'm traveling from Colombo to Kandy by bus tonight at 9pm*")

# user_input = st.text_area("✍️ Describe your trip", value="", height=120, placeholder="Type your travel plan here...")
# submit = st.button("🚦 Assess Trip", use_container_width=True)

# # ----------------- Processing -----------------
# if submit:
#     user_input = sanitize_user_text(user_input)
#     if not user_input.strip():
#         st.error("⚠️ Please enter a trip description.")
#     else:
#         with st.spinner("🔍 Running risk assessment..."):
#             # Risk Agent
#             risk_agent = RiskAssessmentAgent()
#             assessment = risk_agent.handle(user_input)

#         st.markdown("## 📊 Risk Assessment")
#         st.json(assessment)

#         # Advisory Agent
#         st.markdown("## 💡 Advisory")
#         advisory_agent = AdvisoryAgent()
#         advice = advisory_agent.handle(assessment)
#         st.success(f"💬 **Advice:** {advice['advice_text']}")

#         # Emergency Agent
#         st.markdown("## 🚑 Emergency Plan")
#         emergency_agent = EmergencyAgent()
#         emergency_plan = emergency_agent.handle(assessment)
#         st.json(emergency_plan)

#         st.balloons()
#         st.success("✅ Done — results ready for demo/report!")



"""
app.py

Streamlit app with chat-like stylish output (WOW effect).
"""

import streamlit as st
from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
from security import sanitize_user_text, check_token
from dotenv import load_dotenv

load_dotenv()

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="🚦 Trip Safety AI",
    layout="centered",
    page_icon="🚌"
)

# ----------------- Header -----------------
st.title("🚦 Trip Safety AI — Multi-Agent System")
st.caption("🤖 Risk Assessment | 💡 Advisory | 🚑 Emergency Agents (Demo)")

# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("🔑 Authentication")
    token = st.text_input("Admin token (demo)", type="password")
    if not check_token(token):
        st.warning("⚠️ Enter valid admin token to unlock full features.")

    st.markdown("---")
    st.info("ℹ️ This is a demo prototype using AI agents for trip safety.")

# ----------------- Main Input -----------------
st.markdown("### 📝 Enter Trip Details")
st.write("Example: *I'm traveling from Colombo to Kandy by bus tonight at 9pm*")

user_input = st.text_area("✍️ Describe your trip", value="", height=120, placeholder="Type your travel plan here...")
submit = st.button("🚦 Assess Trip", use_container_width=True)

# ----------------- Processing -----------------
if submit:
    user_input = sanitize_user_text(user_input)
    if not user_input.strip():
        st.error("⚠️ Please enter a trip description.")
    else:
        with st.spinner("🔍 Running risk assessment..."):
            # Risk Agent
            risk_agent = RiskAssessmentAgent()
            assessment = risk_agent.handle(user_input)

        # ----------------- Risk Assessment -----------------
        st.markdown("### 📊 Risk Assessment")
        with st.container():
            st.markdown(
                "<div style='background-color:#f0f9ff; padding:15px; border-radius:12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>",
                unsafe_allow_html=True
            )
            if isinstance(assessment, dict):
                for key, value in assessment.items():
                    st.markdown(f"🔹 **{key.replace('_',' ').title()}**: {value}")
            else:
                st.write(assessment)
            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------- Advisory -----------------
        st.markdown("### 💡 Advisory")
        advisory_agent = AdvisoryAgent()
        advice = advisory_agent.handle(assessment)

        with st.container():
            st.markdown(
                "<div style='background-color:#fef9e7; padding:15px; border-radius:12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>",
                unsafe_allow_html=True
            )
            st.markdown(f"💬 **Advice:** {advice['advice_text']}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------- Emergency Plan -----------------
        st.markdown("### 🚑 Emergency Plan")
        emergency_agent = EmergencyAgent()
        emergency_plan = emergency_agent.handle(assessment)

        with st.container():
            st.markdown(
                "<div style='background-color:#f9f9f9; padding:15px; border-radius:12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>",
                unsafe_allow_html=True
            )
            if isinstance(emergency_plan, dict):
                for key, value in emergency_plan.items():
                    st.markdown(f"🚨 **{key.replace('_',' ').title()}**: {value}")
            else:
                st.write(emergency_plan)
            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------- Finish -----------------
        st.success("✅ Done — results ready for demo/report!")
        st.balloons()



