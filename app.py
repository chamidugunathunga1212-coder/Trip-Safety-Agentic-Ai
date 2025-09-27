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

    # ----------------- Commercialization / Pricing Button -----------------
    show_pricing = st.button("💰 View Pro Plans")

# ----------------- Show Pricing if Button Clicked -----------------
if "pricing_visible" not in st.session_state:
    st.session_state["pricing_visible"] = False

if show_pricing:
    st.session_state["pricing_visible"] = not st.session_state["pricing_visible"]

if st.session_state["pricing_visible"]:
    st.markdown("## 💰 Pro & Commercial Plans")
    st.markdown(
        """
        <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:250px; background:#f0f9ff; padding:20px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h3>🚀 Free Plan</h3>
                <ul>
                    <li>✔ Basic risk assessment</li>
                    <li>✔ Advisory recommendations</li>
                    <li>❌ No emergency agent</li>
                    <li>❌ No advanced analytics</li>
                </ul>
                <h4>Price: $0</h4>
            </div>
            
            <div style="flex:1; min-width:250px; background:#fef9e7; padding:20px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h3>💼 Pro Plan</h3>
                <ul>
                    <li>✔ Full risk assessment</li>
                    <li>✔ Advisory + Emergency support</li>
                    <li>✔ Export reports (PDF/CSV)</li>
                    <li>❌ No enterprise features</li>
                </ul>
                <h4>Price: $19/month</h4>
            </div>

            <div style="flex:1; min-width:250px; background:#f9f9f9; padding:20px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h3>🏢 Enterprise</h3>
                <ul>
                    <li>✔ All Pro features</li>
                    <li>✔ Team accounts & dashboards</li>
                    <li>✔ Priority support</li>
                    <li>✔ Custom integrations</li>
                </ul>
                <h4>Contact Sales</h4>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.success("✨ Upgrade to Pro or Enterprise to unlock full potential!")

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
