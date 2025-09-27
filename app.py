"""
app.py
Trip Safety AI — polished UI with cards, icons, and a gauge.
"""

import json
import re
import streamlit as st
from dotenv import load_dotenv

# App logic
from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
from security import (
    sanitize_user_text, get_login_status, init_google_oauth,
    handle_oauth_callback, logout
)

# UI helpers
from ui_components import (
    header, badge, metric_cards, risk_gauge,
    reasons_list, actions_checklist,
    emergency_cards, raw_blocks, navigation_bar
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "home"

load_dotenv()

# Show navigation bar
navigation_bar()

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="🚦 Trip Safety AI",
    layout="wide",  # Changed to wide layout for better navigation
    page_icon="🚌",
    initial_sidebar_state="expanded"  # Always show sidebar
)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Handle OAuth callback
if "code" in st.query_params:
    if handle_oauth_callback(st.query_params["code"]):
        st.rerun()

# ----------------- Styles -----------------
try:
    with open("styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ----------------- Robust JSON extraction helpers -----------------
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.S)

def coerce_to_dict(obj):
    """Return a dict from obj which may be a dict, a JSON string, or a string
    containing a ```json ...``` block. If parsing fails, return {}."""
    if isinstance(obj, dict):
        return obj
    if not isinstance(obj, str):
        return {}

    text = obj.strip()

    # If it's a fenced code block like ```json ... ```
    if text.startswith("```"):
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if not p:
                continue
            # drop leading 'json' / 'JSON'
            if p.lower().startswith("json"):
                p = p[4:].strip()
            try:
                return json.loads(p)
            except Exception:
                m = _JSON_OBJECT_RE.search(p)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except Exception:
                        pass
        return {}

    # If it's plain text with an embedded {...}
    m = _JSON_OBJECT_RE.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # Last resort: try full string as JSON
    try:
        return json.loads(text)
    except Exception:
        return {}

def normalize_emergency(obj):
    """Turn whatever the emergency agent returned into a structured dict."""
    d = coerce_to_dict(obj)
    # If the dict still contains a raw JSON string, parse that too
    for k in ("raw_text", "raw", "emergency_plan"):
        if isinstance(d.get(k), (str, bytes)):
            parsed = coerce_to_dict(d[k])
            if parsed:
                return parsed
    return d

# ----------------- User Authentication -----------------
login_status = get_login_status()

# Check if user is logged in
if not login_status['logged_in']:
    st.markdown("### Welcome to Trip Safety AI")
    st.markdown("Please sign in to access the application features.")
    
    # Center the sign-in button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        flow = init_google_oauth()
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        if st.button("Sign in with Google", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
    st.stop()

# If user is logged in, show the main application
# ----------------- Header -----------------
header(
    title="Trip Safety AI — Multi-Agent System",
    subtitle="• Risk Assessment • Advisory • Emergency Agents (Demo)",
    emoji="🚦"
)

# Add minimal navigation for profile access
col1, col2 = st.columns([6, 1])
with col2:
    user = login_status['user_info']
    if st.button("�", help="View Profile"):
        st.session_state.page = "profile"

# Handle different pages
if st.session_state.page == "profile":
    # Show full navigation in sidebar when in profile
    with st.sidebar:
        st.markdown("### Navigation")
        selected = st.radio(
            "",
            [
                "Profile",
                "Home",
                "Risk Assessment",
                "Price Plan",
                "About",
                "Contact"
            ],
            label_visibility="collapsed"
        )
        
        if selected == "Profile":
            st.session_state.page = "profile"
        elif selected == "Home":
            st.session_state.page = "home"
            st.rerun()
        elif selected == "Risk Assessment":
            st.session_state.page = "risk"
            st.rerun()
        elif selected == "Price Plan":
            st.session_state.page = "pricing"
            st.rerun()
        elif selected == "About":
            st.session_state.page = "about"
            st.rerun()
        elif selected == "Contact":
            st.session_state.page = "contact"
            st.rerun()
    
    # Profile content
    st.markdown("### User Profile")
    if login_status['logged_in']:
        user = login_status['user_info']
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(user['picture'], width=150)
        with col2:
            st.markdown(f"### {user['name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown("---")
            if st.button("Sign Out", use_container_width=True):
                logout()
                st.rerun()
    else:
        st.warning("Please sign in to view your profile.")

elif st.session_state.page == "home":
    st.markdown("### Welcome to Trip Safety AI")
    st.markdown("""
    This application helps you assess and plan for safe travel. Use the navigation 
    bar to access different features:
    
    - **Risk Assessment**: Get detailed safety analysis for your trip
    - **Price Plan**: View our pricing options
    - **About**: Learn more about our service
    - **Contact**: Get in touch with us
    """)
    
elif st.session_state.page == "about":
    st.markdown("### About Trip Safety AI")
    st.markdown("""
    Trip Safety AI is an intelligent system that helps travelers make informed decisions 
    about their journey. Our multi-agent system combines:
    
    - 🤖 Risk Assessment Agent
    - 💡 Advisory Agent
    - 🚑 Emergency Response Agent
    
    Together, these agents provide comprehensive travel safety analysis and recommendations.
    """)
    
elif st.session_state.page == "pricing":
    st.markdown("### 💰 Price Plans")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🌟 Basic
        **$9.99/month**
        
        - Basic risk assessment
        - Standard response time
        - Email support
        - 100 trips/month
        """)
        st.button("Choose Basic", key="basic_plan", use_container_width=True)
        
    with col2:
        st.markdown("""
        ### ✨ Premium
        **$19.99/month**
        
        - Advanced risk assessment
        - Priority response time
        - 24/7 chat support
        - Unlimited trips
        - Weather alerts
        """)
        st.button("Choose Premium", key="premium_plan", use_container_width=True)
        
    with col3:
        st.markdown("""
        ### 💎 Enterprise
        **Custom pricing**
        
        - Custom risk models
        - Dedicated support
        - API access
        - Custom integration
        - Team management
        """)
        st.button("Contact Sales", key="enterprise_plan", use_container_width=True)

elif st.session_state.page == "contact":
    st.markdown("### Contact Us")
    st.markdown("""
    Need help or have questions? Reach out to us:
    
    - 📧 Email: support@tripsafety.ai
    - 📞 Phone: 071-1111111
    - 💬 Chat: Available 24/7 through our website
    """)
    
elif st.session_state.page == "risk":
    # Continue with the original risk assessment functionality
    
    # Add developer options in sidebar
    with st.sidebar:
        st.markdown("---")
        st.info("This is a demo prototype using AI agents for trip safety.")
        show_raw = st.toggle("Developer: show raw data", value=False)

    # ----------------- Main Input -----------------
    st.markdown("### 📝 Enter Trip Details")
    st.caption("Example: *I'm traveling from Colombo to Kandy by bus tonight at 9pm*")

    user_input = st.text_area(
        "✍️ Describe your trip",
        value="",
        height=120,
        placeholder="Type your travel plan here…",
        key="trip_description"
    )

    submit = st.button("🚦 Assess Trip", use_container_width=True)

    # ----------------- Processing -----------------
    if submit:
        user_input = sanitize_user_text(user_input)
        if not user_input.strip():
            st.error("⚠️ Please enter a trip description.")
            st.stop()

        with st.spinner("🔍 Running risk assessment…"):
            risk_agent = RiskAssessmentAgent()
            assessment = risk_agent.handle(user_input)

        # ---- Normalize whatever came back ----
        assessment_dict = coerce_to_dict(assessment)

        # Some repos put info under 'summary'; others at top-level; and sometimes 'summary' is a string
        summary_raw = assessment_dict.get("summary", assessment_dict)
        summary = coerce_to_dict(summary_raw)

        weather_data = coerce_to_dict(
            assessment_dict.get("weather_data") or assessment_dict.get("weather") or {}
        )
        emergency_data_from_risk = normalize_emergency(
            assessment_dict.get("emergency_data") or {}
        )

        # ---- Safe reads with defaults ----
        locations = summary.get("locations", [])
        time_text = summary.get("time", "")
        transport = summary.get("transport_mode", "")

        score = summary.get("risk_score_final", summary.get("risk_score", 0))
        try:
            score = int(score)
        except Exception:
            score = 0

        level = summary.get("risk_level", "Medium")
        reasons = summary.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        actions = summary.get("recommended_actions", [])
        if isinstance(actions, str):
            actions = [actions]

        # ----------------- Summary Cards -----------------
        with st.container(border=True):
            st.caption("Trip overview")
            metric_cards(score=score, level=level, transport=transport, time_text=time_text)
            risk_gauge(score=score, level=level)
            st.markdown(f"**Locations:** {' → '.join(locations) if locations else '—'}")

        # ----------------- Why & What to do -----------------
        with st.container(border=True):
            reasons_list(reasons)
            actions_checklist(actions)

        # ----------------- Advisory -----------------
        st.subheader("💡 Advisory")
        advisory_agent = AdvisoryAgent()
        advice_raw = advisory_agent.handle(summary)  # pass normalized summary
        advice = advice_raw if isinstance(advice_raw, dict) else coerce_to_dict(advice_raw)
        advice_text = advice.get("advice_text") or advice.get("advice") or advice_raw
        with st.container(border=True):
            st.markdown(str(advice_text))

        # ----------------- Emergency Plan -----------------
        st.subheader("🚑 Emergency Plan")
        emergency_agent = EmergencyAgent()
        ctx_for_emergency = summary if summary else assessment_dict  # never undefined
        emergency_raw = emergency_agent.handle(ctx_for_emergency)

        # Normalize strings like ```json {...}``` or dicts that only contain raw_text
        emergency_plan = normalize_emergency(emergency_raw)

        # If the risk agent also provided emergency data, prefer the structured one
        merged_emergency = emergency_plan or emergency_data_from_risk

        # Render nicely (cards); if nothing parsable, show the raw text as a last resort
        if merged_emergency:
            emergency_cards(merged_emergency)
        else:
            st.code(str(emergency_raw))

        # ----------------- Developer raw blocks -----------------
        if show_raw and get_login_status()['logged_in']:
            raw_blocks(summary=summary, weather=weather_data, emergency=merged_emergency)

        st.balloons()
        st.success("✅ Done — results ready for demo/report!")

