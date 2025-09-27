# ui_components.py
# Reusable Streamlit widgets for a clean, visual UI.

import streamlit as st
import plotly.graph_objects as go

# ---------- Theme ----------
RISK_COLORS = {"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e74c3c"}

def navigation_bar():
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #2196f3;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            color: white !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: white;
            color: #2196f3;
        }
        section[data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    with st.sidebar:
        st.markdown("### Navigation")
        nav_items = {
            "Home": "home",
            "Risk Assessment": "risk",
            "Price Plan": "pricing",
            "About": "about",
            "Contact": "contact"
        }
        
        current_page = st.session_state.get('page', 'home')
        for label, page in nav_items.items():
            if st.button(
                label,
                use_container_width=True,
                type="primary" if current_page == page else "secondary"
            ):
                st.session_state.page = page
                st.rerun()

# ---------- Header ----------
def header(title=None, subtitle=None, emoji="", anim=None):
    col1, col2 = st.columns([2, 8])
    with col1:
        try:
            st.image("static/images/logo.png", width=200)  # bigger logo
        except Exception:
            if emoji:
                st.markdown(f"<div style='font-size:36px'>{emoji}</div>", unsafe_allow_html=True)
    with col2:
        # Hide title + subtitle on purpose (only logo)
        if title and st.session_state.page != "home":
            st.markdown(f"## {title}")
        if subtitle and st.session_state.page != "home":
            st.caption(subtitle)
    st.divider()

# ---------- Metric Cards ----------
def metric_cards(score:int, level:str, transport:str, time_text:str):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risk Score", f"{int(score)}/100")
    c2.metric("Risk Level", level)
    c3.metric("Transport", transport.capitalize() if transport else "—")
    c4.metric("When", time_text or "—")

# ---------- Risk Gauge ----------
def risk_gauge(score:int, level:str):
    color = RISK_COLORS.get(level, "#95a5a6")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(score or 0),
        number={'suffix': " / 100"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color, 'thickness': 0.35},
            'steps': [
                {'range': [0, 40], 'color': '#eafaf1'},
                {'range': [40, 70], 'color': '#fff7df'},
                {'range': [70, 100], 'color': '#ffe6e3'}
            ]
        }
    ))
    fig.update_layout(height=230, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---------- Icons ----------
ICON_MAP = {
    "thunder": "⛈️", "storm": "⛈️", "rain": "🌧️", "night": "🌙", "visibility": "👁️",
    "fatigue": "😴", "incident": "🚧", "road": "🛣️", "emergency": "🚑", "wind": "🌬️",
    "heat": "🌡️", "slippery": "⚠️", "default": "📌",
}
def icon_for(text:str):
    t = (text or "").lower()
    for k, v in ICON_MAP.items():
        if k in t:
            return v
    return ICON_MAP["default"]

# ---------- Reasons ----------
def reasons_list(reasons:list[str]):
    st.subheader("Why this risk?")
    if not reasons:
        st.write("—")
        return
    for r in reasons:
        st.markdown(f"- {icon_for(r)} {r}")

# ---------- Actions Checklist ----------
def actions_checklist(actions:list[str]):
    st.subheader("Recommended actions")
    if not actions:
        st.write("—")
        return
    for a in actions:
        st.checkbox(a, value=False, key=f"action_{hash(a)}")

# ---------- Emergency Cards ----------
def emergency_cards(emergency_data):
    st.subheader("")

    if not emergency_data:
        st.info("No emergency data available.")
        return

    if isinstance(emergency_data, list):
        for plan in emergency_data:
            if not isinstance(plan, dict):
                st.write(plan)
                continue

            location = plan.get("location", "Unknown Location")
            contacts = plan.get("emergency_contacts", {})
            steps = plan.get("next_steps", [])
            checklist = plan.get("3-min_response_checklist", [])

            with st.container(border=True):
                st.markdown(f"### 📍 {location}")

                if contacts:
                    st.markdown("**☎️ Emergency Contacts:**")
                    for label, num in contacts.items():
                        icon = "🚓" if "police" in label else "🚑" if "ambulance" in label else "🔥" if "fire" in label else "☎️"
                        st.markdown(f"- {icon} **{label.replace('_',' ').title()}:** {num}")

                if steps:
                    st.markdown("**✅ Next Steps:**")
                    for step in steps:
                        st.markdown(f"- {step}")

                if checklist:
                    st.markdown("**🕒 3-Minute Response Checklist:**")
                    for step in checklist:
                        st.markdown(f"- {step}")

    elif isinstance(emergency_data, dict):
        for city, info in emergency_data.items():
            with st.container(border=True):
                st.markdown(f"### 📍 {city}")
                if isinstance(info, dict):
                    for label, num in (info.get("emergency_contacts") or {}).items():
                        st.markdown(f"- **{label}:** {num}")
                    for step in info.get("next_steps", []):
                        st.markdown(f"- {step}")
                else:
                    st.write(info)
    else:
        st.write(emergency_data)

# ---------- Raw Blocks ----------
def raw_blocks(summary:dict=None, weather:dict=None, emergency:dict=None):
    with st.expander("Raw summary JSON"):
        st.json(summary or {})
    with st.expander("Raw weather sources"):
        st.json(weather or {})
    with st.expander("Raw emergency sources"):
        st.json(emergency or {})
