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
from security import sanitize_user_text, check_token

# UI helpers
from ui_components import (
    header, badge, metric_cards, risk_gauge,
    reasons_list, actions_checklist,
    emergency_cards, raw_blocks
)

load_dotenv()

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="🚦 Trip Safety AI",
    layout="centered",
    page_icon="🚌"
)

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

# ----------------- Header -----------------
header(
    title="Trip Safety AI — Multi-Agent System",
    subtitle="🤖 Risk Assessment • 💡 Advisory • 🚑 Emergency Agents (Demo)",
    emoji="🚦"
)

# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("🔑 Authentication")
    token = st.text_input("Admin token (demo)", type="password")
    is_admin = check_token(token)
    if not is_admin:
        st.warning("Enter a valid admin token to unlock full features.")
    st.markdown("---")
    st.info("This is a demo prototype using AI agents for trip safety.")
    show_raw = st.toggle("Developer: show raw data", value=False if not is_admin else False)

# ----------------- Main Input -----------------
st.markdown("### 📝 Enter Trip Details")
st.caption("Example: *I'm traveling from Colombo to Kandy by bus tonight at 9pm*")

user_input = st.text_area(
    "✍️ Describe your trip",
    value="",
    height=120,
    placeholder="Type your travel plan here…"
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
    if show_raw and is_admin:
        raw_blocks(summary=summary, weather=weather_data, emergency=merged_emergency)

    st.balloons()
    st.success("✅ Done — results ready for demo/report!")
