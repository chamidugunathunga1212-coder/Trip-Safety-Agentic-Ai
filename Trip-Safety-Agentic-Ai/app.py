import json, re
import streamlit as st
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate

# Agents & utilities
from agents import RiskAssessmentAgent, AdvisoryAgent, EmergencyAgent
from security import sanitize_user_text
from ui_components import (
    header, metric_cards, risk_gauge,
    reasons_list, actions_checklist,
    emergency_cards, raw_blocks, navigation_bar
)

# ----------------- JSON Utility Helpers -----------------
_JSON_OBJECT_OR_ARRAY_RE = re.compile(r"(\{.*\}|\[.*\])", re.S)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.S)
def coerce_to_dict(obj):
    """Ensure the object is converted safely into a Python dictionary."""
    import json

    # Case 1: Already a dict
    if isinstance(obj, dict):
        return obj

    # Case 2: It's a string that looks like JSON
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            return {"text": obj}

    # Case 3: Has a to_dict() method
    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    # Case 4: Fallback
    return {"data": obj}

def coerce_json_any(obj):
    if isinstance(obj, (dict, list)):
        return obj
    if not isinstance(obj, str):
        return {}
    s = obj.strip()
    try:
        return json.loads(s)
    except:
        m = _JSON_OBJECT_OR_ARRAY_RE.search(s)
        if m:
            try:
                return json.loads(m.group(1))
            except:
                return {}
        return {}

def normalize_emergency(obj):
    data = coerce_json_any(obj)
    if isinstance(data, dict):
        for k in ("emergency_plan", "raw_text", "raw"):
            v = data.get(k)
            if v is not None:
                data = coerce_json_any(v)
        if isinstance(data, dict) and isinstance(data.get("locations"), list):
            return data["locations"]
        return data
    if isinstance(data, list):
        return data
    return []


# ----------------- Setup -----------------
st.set_page_config(
    page_title="Trip Safety AI",
    layout="wide",
    page_icon="static/images/logo.png",
    initial_sidebar_state="expanded"
)

# ----------------- Authentication -----------------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# ----------------- Session State -----------------
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

# ----------------- Helper Navigation -----------------

def go_login():
    st.session_state["page"] = "login"
    st.session_state["login_username"] = ""
    st.session_state["login_password"] = ""
    st.rerun()

   
def go_register():
    st.session_state["page"] = "register"
    
def go_home():
    st.session_state["page"] = "home"
   
def logout_user():
    st.session_state["authentication_status"] = False
    st.session_state["username"] = None
    st.session_state["name"] = None
    st.success("👋 Logged out successfully! You can now log in again.")
    st.rerun()

def validate_password(password):
    """🧩 Validate password strength."""
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one digit."
    return None


import bcrypt

def save_new_user(username, name, password):
    """Create a new user entry and save it to config.yaml."""
    if not username or not password or not name:
        return False, "All fields are required."

    # Load current users
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    users = config.get("credentials", {}).get("usernames", {})
    if username in users:
        return False, "Username already exists."

    # --- Hash password using bcrypt ---
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Save new user
    users[username] = {
        "name": name,
        "password": hashed_password
    }

    config["credentials"]["usernames"] = users

    # Write back to YAML file
    with open("config.yaml", "w") as file:
        yaml.safe_dump(config, file)

    return True, "Account created successfully."


# ----------------- NAVIGATION BAR -----------------
load_dotenv()
navigation_bar()  # ← uses your existing sidebar function (no extra_items)


# --------------------------
# LOGIN PAGE
# --------------------------
import bcrypt
import yaml
import streamlit as st

# ---------------- LOGIN PAGE ----------------
if st.session_state.get("page") == "login":
    # ✅ If user already logged in → show welcome banner
    if st.session_state.get("authentication_status"):
        user_name = st.session_state.get("name", "User")

        # --- Stylish Welcome Card ---
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #6a11cb, #2575fc);
                padding: 30px;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            ">
                <h2 style="margin-bottom: 10px;">👋 Welcome back, <b>{user_name}</b>!</h2>
                <p>You are now logged in to <b>Safari-Trip Safety AI</b>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Logout button (styled separately for clean layout)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                st.session_state.clear()
                st.session_state["page"] = "login"
                st.rerun()

    else:
        # 🔹 Normal login form (only shown if NOT logged in)
        st.markdown("### 🔐 Login to Sawari - Trip Safety AI")

        username_input = st.text_input(
            "👤 Username",
            key="login_username",
            placeholder="Enter your username",
            label_visibility="visible",
        )

        password_input = st.text_input(
            "🔑 Password",
            key="login_password",
            placeholder="Enter your password",
            type="password",
            label_visibility="visible",
        )

        if st.button("🔓 Login", key="login_btn", use_container_width=True):
            if not username_input or not password_input:
                st.warning("⚠️ Please enter both username and password.")
            else:
                with open("config.yaml", "r") as file:
                    config = yaml.safe_load(file)

                users = config.get("credentials", {}).get("usernames", {})

                if username_input in users:
                    hashed_pw = users[username_input]["password"].encode()
                    if bcrypt.checkpw(password_input.encode(), hashed_pw):
                        st.session_state["authentication_status"] = True
                        st.session_state["name"] = users[username_input]["name"]
                        st.rerun()  # Refresh to show welcome banner
                    else:
                        st.error("🚫 Invalid password.")
                else:
                    st.error("🚫 Username not found.")

        # Navigation buttons
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("⬅️ Back to Home", key="back_home_login", on_click=go_home)
        st.button("🆕 Create Account", key="create_acc_btn", on_click=go_register)



# ----------------- HOME PAGE -----------------
elif st.session_state["page"] == "home":
    st.markdown("""
    <style>
    .home-hero {
        background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e');
        background-size: cover;
        background-position: center;
        padding: 120px 40px;
        border-radius: 15px;
        color: white;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    }
    </style>
    <div class="home-hero">
        <h1>Welcome to Trip Safety AI</h1>
        <p>Use the navigation bar to explore:</p>
        <ul>
            <li><b>Risk Assessment</b></li>
            <li><b>Price Plan</b></li>
            <li><b>About</b></li>
            <li><b>Contact</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------- OTHER PAGES -----------------
elif st.session_state["page"] == "about":
    about_html = f"""
    <div style="
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        max-width: 600px;
        margin: auto;
        font-family: sans-serif;
    ">
        <h2 style="margin-bottom: 15px;">ℹ️ About Trip Safety AI</h2>
        <p style="text-align: left; margin: 0 40px;">
            Trip Safety AI helps travelers make informed decisions using:
        </p>
        <ul style="text-align: left; margin: 10px 60px;">
            <li>🤖 <b>Risk Assessment Agent</b></li>
            <li>💡 <b>Advisory Agent</b></li>
            <li>🚑 <b>Emergency Response Agent</b></li>
        </ul>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)



# CREATE ACCOUNT PAGE ---------------------------------

# import bcrypt
elif st.session_state["page"] == "register":
    st.markdown("### 🆕 Create New Account")

    # Input fields
    name = st.text_input("👤 Full Name")
    username = st.text_input("🧾 Username")
    password = st.text_input("🔑 Password", type="password")
    confirm_password = st.text_input("🔒 Confirm Password", type="password")

    # --- Real-time validation feedback ---
    if name and len(name) < 3:
        st.warning("⚠️ Full name should be at least 3 characters long.")

    if username:
        if len(username) < 3:
            st.warning("⚠️ Username must be at least 3 characters long.")
        elif not username.isalnum():
            st.warning("⚠️ Username must only contain letters and numbers.")

    if password:
        if len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters long.")
        elif password.isalpha() or password.isdigit():
            st.warning("⚠️ Password must include both letters and numbers.")

    if confirm_password and password != confirm_password:
        st.error("❌ Passwords do not match.")

    # --- Load existing users ---
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    users = config.get("credentials", {}).get("usernames", {})

    # Check for duplicate username (live)
    if username and username in users:
        st.error("🚫 Username already exists. Please choose another one.")

    # --- Enable button only if all valid ---
    is_valid = (
        name
        and username
        and password
        and confirm_password
        and password == confirm_password
        and len(password) >= 6
        and username not in users
    )

    # Disable button until everything valid
    create_button = st.button("✅ Create Account", key="final_create", disabled=not is_valid)

    if create_button and is_valid:
        # Hash password securely
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Update YAML config
        if "credentials" not in config:
            config["credentials"] = {}
        if "usernames" not in config["credentials"]:
            config["credentials"]["usernames"] = {}

        config["credentials"]["usernames"][username] = {
            "name": name,
            "password": hashed_pw,
        }

        with open("config.yaml", "w") as file:
            yaml.dump(config, file)

        st.success("🎉 Account created successfully! You can now log in.")
        st.session_state["page"] = "login"
        st.rerun()

    st.button("⬅️ Back to Login", key="back_login_btn", on_click=go_login)


elif st.session_state["page"] == "pricing":
    st.markdown("### Pricing Plans")

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
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
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="pricing-card" style="background-color:#4b185f; border:2px solid #ff007f;">
                <h2>Enterprise</h2>
                <h3>$10 / month</h3>
                <ul>
                    <li>✔ Unlimited tokens</li>
                    <li>✔ Full AI advisory</li>
                    <li>✔ PDF trip safety reports</li>
                    <li>✔ API & analytics dashboard</li>
                </ul>
                <br>
                <button class="pricing-btn">Order Now</button>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----contact page----
elif st.session_state["page"] == "contact":
    contact_html = f"""
    <div style="
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        max-width: 500px;
        margin: auto;
        font-family: sans-serif;
    ">
        <h2 style="margin-bottom: 10px;">Contact Us</h2>
        <p>Email: <a href="mailto:support@tripsafety.ai" style="color:white; text-decoration:underline;">support@tripsafety.ai</a></p>
        <p>Phone: <a href="tel:+94711111111" style="color:white; text-decoration:underline;">+94 71 1111111</a></p>
    </div>
    """
    st.markdown(contact_html, unsafe_allow_html=True)


# ---risk page---
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

        weather_data = coerce_to_dict(
            assessment_dict.get("weather_data") or assessment_dict.get("weather") or {}
        )
        emergency_data_from_risk = normalize_emergency(
            assessment_dict.get("emergency_data") or {}
        )

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
        emergency_result = emergency_agent.handle(summary)
        merged_emergency = normalize_emergency(emergency_result)

        if not merged_emergency:
            merged_emergency = emergency_data_from_risk

        if merged_emergency:
            emergency_cards(merged_emergency)
        else:
            st.write("No emergency plan available")

        if show_raw:
            raw_blocks(summary, weather_data, merged_emergency)

        st.success("✅ Done!")



