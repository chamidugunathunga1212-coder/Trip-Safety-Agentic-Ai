"""
utils.py

Helper functions: risk scoring, summarization, etc.
"""

from typing import Dict, Any
import re
import math

def compute_risk_score(weather_data: Dict[str, Any], emergency_data: Dict[str, Any], transport: str) -> int:
    """
    Very simple deterministic heuristic score (0-100).
    In your final report, explain that this is a heuristic and can be replaced with ML.
    """
    base = 20
    # if weather suggests severe words
    severe_words = ["storm", "heavy rain", "flood", "cyclone", "hurricane", "severe", "snow"]
    for loc, wd in (weather_data or {}).items():
        raw = str(wd.get("raw", "")).lower()
        for w in severe_words:
            if w in raw:
                base += 30
                break
    # emergency data mentions 'closure'/'accident' add points
    for loc, ed in (emergency_data or {}).items():
        raw = str(ed.get("raw", "")).lower()
        if "accident" in raw or "closure" in raw or "evacuat" in raw:
            base += 25
    # transport risk
    if transport in ("bus", "train", "motorbike", "car"):
        base += 10
    if transport in ("flight", "plane"):
        base += 5
    # clamp
    score = max(0, min(100, base))
    return score

def summarize_text(text: str, max_sentences:int = 2) -> str:
    if not text:
        return "No text to summarize."
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sents[:max_sentences]).strip()

