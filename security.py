"""
security.py

- sanitize_user_text: small sanitizer to remove suspicious patterns
- simple token-based auth for Streamlit demo
"""

import re
from typing import Tuple
from dotenv import load_dotenv
import os
load_dotenv()

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme_admin_token")

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

def check_token(token: str) -> bool:
    return token == ADMIN_TOKEN
