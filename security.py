# security.py
import re

def sanitize_user_text(text: str, max_len: int = 2000) -> str:
    t = text.strip()
    if len(t) > max_len:
        t = t[:max_len]
    t = re.sub(r'(http|https|file):\/\/\S+', '[REDACTED_URL]', t, flags=re.I)
    t = re.sub(r'<\s*script.*?>.*?<\s*/\s*script\s*>', '', t, flags=re.I|re.S)
    t = re.sub(r'[\r\n]{2,}', '\n', t)
    return t
