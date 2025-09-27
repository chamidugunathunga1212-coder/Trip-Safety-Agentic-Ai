# app.py
import json, re
import streamlit as st
from dotenv import load_dotenv

# Agents
from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
from security import sanitize_user_text

# UI
from ui_components import (
    header, metric_cards, risk_gauge,
    reasons_list, actions_checklist,
    emergency_cards, raw_blocks, navigation_bar
)

# ----------------- Setup -----------------
st.set_page_config(
    page_title=" Trip Safety AI",
    layout="wide",
    page_icon="static/images/logo.png",
    initial_sidebar_state="expanded"
)


if 'page' not in st.session_state:
    st.session_state.page = "home"

load_dotenv()
navigation_bar()

# Regex for JSON parsing
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.S)

def coerce_to_dict(obj):
    if isinstance(obj, dict): return obj
    if not isinstance(obj, str): return {}
    m = _JSON_OBJECT_RE.search(obj)
    if m:
        try: return json.loads(m.group(0))
        except: return {}
    try: return json.loads(obj)
    except: return {}

def normalize_emergency(obj):
    d = coerce_to_dict(obj)
    for k in ("raw_text", "raw", "emergency_plan"):
        if isinstance(d.get(k), str):
            return coerce_to_dict(d[k])
    return d

# ----------------- Header -----------------
header(
    title="Trip Safety AI \nMulti-Agent System",
    subtitle="• Risk Assessment • Advisory • Emergency Agents (Demo)",
    emoji="🚦"
)

# ----------------- Pages -----------------
if st.session_state.page == "home":
    st.markdown("### Welcome to Trip Safety AI")
    st.markdown("""
    Use the navigation bar to explore:
    - **Risk Assessment**  
    - **Price Plan**  
    - **About**  
    - **Contact**
    """)

elif st.session_state.page == "about":
    st.markdown("### About Trip Safety AI")
    st.markdown("""
    Trip Safety AI helps travelers make informed decisions using:
    - 🤖 Risk Assessment Agent
    - 💡 Advisory Agent
    - 🚑 Emergency Response Agent
    """)

elif st.session_state.page == "pricing":
    st.markdown("###  Pricing Plans")

    # Add custom CSS for gradient hover effects
    st.markdown("""
    <style>
    .pricing-card {
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        transition: all 0.3s ease;
    }
    .pricing-card:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
    }
    .pricing-btn {
        background: #ff007f;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .pricing-btn:hover {
        background: linear-gradient(135deg, #ff4b2b, #ff416c);
        transform: scale(1.1);
    }
    ul { list-style: none; padding: 0; text-align: left; margin-top: 20px; }
    li { margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="pricing-card" style="background-color:#1a1a40;">
            <h2>Primary</h2>
            <h3>$0 / week</h3>
            <ul>
                <li>✔ Up to 5,000 tokens/week</li>
                <li>✔ Basic risk score</li>
                <li>✔ Simple advisory</li>
                <li>✔ Emergency contacts</li>
            </ul>
            <br>
            <button class="pricing-btn">Get Started</button>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card" style="background-color:#4b185f; border:2px solid #ff007f;">
            <h2>Enterprise</h2>
            <h3>$10 / week</h3>
            <ul>
                <li>✔ Unlimited tokens</li>
                <li>✔ Full AI advisory</li>
                <li>✔ PDF trip safety reports</li>
                <li>✔ API & analytics dashboard</li>
            </ul>
            <br>
            <button class="pricing-btn">Order Now</button>
        </div>
        """, unsafe_allow_html=True)



elif st.session_state.page == "contact":
    st.markdown("### Contact Us")
    st.markdown("📧 support@tripsafety.ai | 📞 071-1111111")

elif st.session_state.page == "risk":
    with st.sidebar:
        show_raw = st.toggle("Developer: show raw data", value=False)

    st.markdown("### 📝 Enter Trip Details")
    user_input = st.text_area("✍️ Describe your trip", height=120)
    submit = st.button("🚦 Assess Trip", use_container_width=True)

    if submit:
        user_input = sanitize_user_text(user_input)
        if not user_input.strip():
            st.error("⚠️ Please enter a trip description.")
            st.stop()

        with st.spinner("🔍 Running risk assessment…"):
            risk_agent = RiskAssessmentAgent()
            assessment = risk_agent.handle(user_input)

        assessment_dict = coerce_to_dict(assessment)
        summary = coerce_to_dict(assessment_dict.get("summary", assessment_dict))
        weather_data = coerce_to_dict(assessment_dict.get("weather") or {})
        emergency_data_from_risk = normalize_emergency(assessment_dict.get("emergency_data") or {})

        locations = summary.get("locations", [])
        time_text = summary.get("time", "")
        transport = summary.get("transport_mode", "")
        score = int(summary.get("risk_score_final", summary.get("risk_score", 0)) or 0)
        level = summary.get("risk_level", "Medium")
        reasons = summary.get("reasons", [])
        if isinstance(reasons, str): reasons = [reasons]
        actions = summary.get("recommended_actions", [])
        if isinstance(actions, str): actions = [actions]

        with st.container(border=True):
            metric_cards(score, level, transport, time_text)
            risk_gauge(score, level)
            st.markdown(f"**Locations:** {' → '.join(locations) if locations else '—'}")

        with st.container(border=True):
            reasons_list(reasons)
            actions_checklist(actions)

        st.subheader("💡 Advisory")
        advisory_agent = AdvisoryAgent()
        advice = coerce_to_dict(advisory_agent.handle(summary))
        st.markdown(str(advice.get("advice_text") or advice.get("advice") or advice))

        st.subheader("🚑 Emergency Plan")
        emergency_agent = EmergencyAgent()
        emergency_plan = normalize_emergency(emergency_agent.handle(summary))
        merged_emergency = emergency_plan or emergency_data_from_risk
        if merged_emergency:
            emergency_cards(merged_emergency)
        else:
            st.write("No emergency plan available")

        if show_raw:
            raw_blocks(summary, weather_data, merged_emergency)

        st.success("✅ Done!")

