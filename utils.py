"""
utils.py
Risk scoring helper with ML + manual fallback.
Same function signature as the old version.
"""

from typing import Dict, Any
import re
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor


# Train ML model once (using dataset)

df = pd.read_csv("E:\\Trip-Safety-Agentic-Ai\\sri_lanka_accidents_dataset.csv")

# drop target
X = df.drop(columns=["accident_probability"])
y = df["accident_probability"]

# label encode object columns
encoders = {}
for col in X.select_dtypes(include="object").columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

# train small model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

print("✅ Model trained successfully with", len(df), "records.")

# ----------------------------------------------------------
def compute_risk_score(weather_data: Dict[str, Any],
                       emergency_data: Dict[str, Any],
                       transport: str) -> float:
    """
    Compute risk score (0–100).
    1️⃣ Try ML model prediction using available inputs.
    2️⃣ If unseen or missing data → fallback to manual heuristic.
    """
    # --- Step 1: Build minimal ML sample ---
    try:
        # Prepare safe default sample (using most common values from dataset)
        sample = {
            "City": "Colombo",
            "Transport_Mode": transport,
            "Brand": "Toyota",
            "Weather_Condition": "Clear",
            "Time_of_Day": "Morning",
            "Emergency_Alert": "None",
            "Speed_Limit_kmh": 60,
            "Past_Accidents_in_Region": 25
        }

        # Update from weather_data if possible
        if weather_data:
            w_raw = " ".join([str(v.get("raw", "")) for v in weather_data.values()]).lower()
            if "rain" in w_raw: sample["Weather_Condition"] = "Rain"
            if "heavy rain" in w_raw or "storm" in w_raw: sample["Weather_Condition"] = "Heavy Rain"
            if "fog" in w_raw: sample["Weather_Condition"] = "Fog"

        # Update from emergency_data if possible
        if emergency_data:
            e_raw = " ".join([str(v.get("raw", "")) for v in emergency_data.values()]).lower()
            if "accident" in e_raw: sample["Emergency_Alert"] = "Accident Nearby"
            elif "flood" in e_raw: sample["Emergency_Alert"] = "Flood Alert"
            elif "closure" in e_raw: sample["Emergency_Alert"] = "Road Closure"

        # Encode the single row
        X_input = pd.DataFrame([sample])
        for col, le in encoders.items():
            X_input[col] = le.transform(X_input[col])

        # Predict probability
        pred = model.predict(X_input)[0]
        return round(pred * 100, 2)

    except Exception:
        # --- Step 2: Manual fallback ---
        base = 20
        severe_words = ["storm", "heavy rain", "flood", "cyclone", "hurricane", "fog", "severe", "snow"]

        # Weather effect
        for loc, wd in (weather_data or {}).items():
            raw = str(wd.get("raw", "")).lower()
            if any(w in raw for w in severe_words):
                base += 30
                break

        # Emergency effect
        for loc, ed in (emergency_data or {}).items():
            raw = str(ed.get("raw", "")).lower()
            if any(k in raw for k in ["accident", "closure", "evacuat", "alert", "landslide"]):
                base += 25

        # Transport-based effect
        t = str(transport).lower()
        if t in ("car", "bus", "van", "jeep", "tuktuk", "threewheel"):
            base += 10
        elif t in ("motorbike", "bike", "bicycle", "scooter"):
            base += 20
        elif t in ("truck", "lorry", "heavy vehicle"):
            base += 15
        elif t in ("train", "metro"):
            base += 5
        elif t in ("boat", "ship"):
            base += 12
        elif t in ("plane", "flight", "aircraft"):
            base += 8
        else:
            base += 5

        return float(max(0, min(100, base)))

# ----------------------------------------------------------
def summarize_text(text: str, max_sentences: int = 2) -> str:
    """Short text summarizer (same as before)."""
    if not text:
        return "No text to summarize."
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sents[:max_sentences]).strip()