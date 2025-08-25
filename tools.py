"""
tools.py

Wrapper for:
- fetch_weather_for_location: uses SERPER (or any external IR) to get weather text.
- fetch_emergency_info_for_location: uses SERPER to get local emergency intel.

Notes:
- Replace the search URLs as needed for your Serper client.
- Keep network calls small and cache responses in production.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_SEARCH_URL = "https://google.serper.dev/search"  # example Serper endpoint (adjust if different)
HEADERS = {"X-API-KEY": SERPER_API_KEY} if SERPER_API_KEY else {}

def fetch_serper(query: str) -> Dict[str, Any]:
    """
    Minimal Serper query. Adapt according to the official Serper client.
    """
    try:
        payload = {"q": query}
        resp = requests.post(SERPER_SEARCH_URL, json=payload, headers=HEADERS, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e), "query": query}

def extract_top_text_from_serper(resp: Dict[str, Any]) -> str:
    # Best-effort extraction depending on Serper response structure
    if not isinstance(resp, dict):
        return str(resp)
    if "organic" in resp and resp["organic"]:
        snippets = [item.get("snippet", "") for item in resp["organic"]][:3]
        return "\n".join(snippets)
    # fallback
    return str(resp)[:1000]

def fetch_weather_for_location(location: str) -> Dict[str, Any]:
    q = f"weather in {location} next 24 hours"
    resp = fetch_serper(q)
    text = extract_top_text_from_serper(resp)
    # simple parse: return the raw text plus a placeholder structured object
    return {"raw": text, "source_query": q}

def fetch_emergency_info_for_location(location: str) -> Dict[str, Any]:
    q = f"emergency services in {location} helpline, recent incidents, road closures"
    resp = fetch_serper(q)
    text = extract_top_text_from_serper(resp)
    return {"raw": text, "source_query": q}
