"""
nlp.py
spaCy-based NER and simple heuristics for transport & time.
"""

import re
from typing import List, Optional
import spacy
from dateutil import parser as date_parser
nlp = None

LOC_ENT_LABELS = {"GPE", "LOC", "FAC", "NORP"}

def _lazy_load_spacy():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            # fallback: download if not present (note: requires internet at setup)
            from spacy.cli import download
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    return nlp

def extract_locations(text: str) -> List[str]:
    n = _lazy_load_spacy()
    doc = n(text)
    locs = [ent.text for ent in doc.ents if ent.label_ in LOC_ENT_LABELS]
    # deduplicate & return
    seen = set()
    out = []
    for l in locs:
        s = l.strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    # heuristic: if none found, try capturing tokens like "Colombo", "Kandy" with capitals
    if not out:
        capitals = re.findall(r"\b([A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})?)\b", text)
        out = capitals[:2]
    return out

def extract_time(text: str) -> Optional[str]:
    # try to parse a date/time in text
    maybe = None
    try:
        # crude: search for common phrases like 'tonight', 'tomorrow', 'at 9pm' etc.
        m = re.search(r"(tonight|tomorrow|today|at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", text, re.I)
        if m:
            maybe = m.group(0)
            # try normalizing 'at 9pm' -> parseable
            try:
                dt = date_parser.parse(maybe, fuzzy=True)
                return dt.isoformat()
            except Exception:
                return maybe
    except Exception:
        return None
    return maybe

def extract_transport_mode(text: str) -> Optional[str]:
    modes = ["bus", "train", "car", "motorbike", "walk", "flight", "plane", "ferry"]
    txt = text.lower()
    for m in modes:
        if m in txt:
            return m
    # fallback
    return None
