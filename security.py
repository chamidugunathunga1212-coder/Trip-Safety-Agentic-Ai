"""
security.py

- sanitize_user_text: small sanitizer to remove suspicious patterns
- Google OAuth authentication
"""

import re
from typing import Dict
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def sanitize_user_text(text: str, max_len: int = 2000) -> str:
    # limit length
    t = text.strip()
    if len(t) > max_len:
        t = t[:max_len]
    # remove dangerous protocol patterns
    t = re.sub(r'(http|https|file):\/\/\S+', '[REDACTED_URL]', t, flags=re.I)
    # remove script tags if any
    t = re.sub(r'<\s*script.*?>.*?<\s*/\s*script\s*>', '', t, flags=re.I|re.S)
    # avoid newlines heavy injection
    t = re.sub(r'[\r\n]{2,}', '\n', t)
    return t

def init_google_oauth():
    """Initialize Google OAuth flow"""
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = REDIRECT_URI  # Explicitly set the redirect URI without trailing slash
    return flow

def get_login_status() -> Dict:
    """Get the current login status"""
    if 'user' not in st.session_state:
        return {'logged_in': False, 'user_info': None}
    return {'logged_in': True, 'user_info': st.session_state.user}

def handle_oauth_callback(code: str):
    """Handle the OAuth callback and store user info in session"""
    try:
        flow = init_google_oauth()
        
        # Fetch the token with the code and redirect URI
        flow.fetch_token(
            code=code,
            authorization_response=REDIRECT_URI
        )
        
        credentials = flow.credentials
        
        # Get user info using the credentials
        from googleapiclient.discovery import build
        
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        st.session_state.user = {
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info['picture']
        }
        return True
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        st.error(f"Please check your Google OAuth configuration and make sure the redirect URI matches exactly.")
        return False

def logout():
    """Clear the user session"""
    if 'user' in st.session_state:
        del st.session_state.user
