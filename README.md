#  Trip Safety AI

Trip Safety AI is an intelligent system that helps travelers evaluate and manage risks associated with their journeys. It uses AI agents, real-time data, and risk scoring models to provide users with personalized safety recommendations before and during a trip.

✨ Features

   &nbsp; &nbsp; 🧠 AI-powered risk assessment

   &nbsp; &nbsp; 🌦️ Weather analysis (storms, floods, extreme temperatures)

   &nbsp; &nbsp; 🛣️ Route safety (traffic, accident zones, road conditions)

   &nbsp; &nbsp; 🦠 Health & disease alerts (COVID, dengue, flu risk by region)

   &nbsp; &nbsp; 📍 Location-based warnings (crime statistics, political unrest, natural disasters)

   &nbsp; &nbsp; 🧭 Personalized travel guidance (suggest safest transport or reschedule trips)

# System Architecture
![irwa](https://github.com/user-attachments/assets/ab3220f2-0eeb-40bc-a9b2-d6a3cefcc554)

# Security workflow
1.limit length

2.remove dangerous protocol patterns
"Check this link: https://evil.com"  
→ "Check this link: [REDACTED_URL]"

3.remove script tags if any
"<script>alert('Hacked!')</script> Hello"  
→ " Hello"

"<ScRiPt>\nconsole.log('test');\n</sCrIpT>"  
→ ""

4.avoid newlines heavy injection
"Hello\n\n\n\nWorld"  
→ "Hello\nWorld"

## ⚙️ Risk Scoring Formula

The Trip Safety AI system calculates the **final risk score (0–100)** by combining both
machine learning predictions and manual heuristic adjustments based on real-world conditions.

\[
\textbf{Risk Score} = W_w \times Weather + W_e \times Emergency + W_t \times Transport
\]

Where:

| Symbol | Factor | Description |
|:--:|:--|:--|
| **Ww** | Weather Weight | Increases score during heavy rain, fog, or storms. |
| **We** | Emergency Weight | Adds extra risk for accidents, floods, or road closures nearby. |
| **Wt** | Transport Weight | Adjusts score based on vehicle type (bike > car > train). |

---


# 🔎 Example Workflow

User input:
  &nbsp; &nbsp;  From: Colombo
  &nbsp; &nbsp;  To: Kandy
  &nbsp; &nbsp;  Date: Tomorrow
  &nbsp; &nbsp;  Transport: Bus

System checks:

Weather API → heavy rain forecast 🌧️

Road safety API → recent landslide alerts 🚧

Health database → dengue outbreak in Kandy ⚠️

Result:

Final Risk Score = High Risk

Recommendation = “Avoid travel. Reschedule trip.”

# Trip Safety AI — Multi-Agent System (Demo)

This project implements a multi-agent Trip Safety AI with:
- Risk Assessment Agent
- Advisory Agent
- Emergency Agent

Stack:
- autogen v0.7 (integrate orchestration if desired)
- OpenAI API (LLM)
- Serper (search/IR for weather & emergency info)
- spaCy for NER
- Streamlit for demo UI

## Setup

1. Create `.env` from `.env.example` and fill keys.
2. Python 3.10+ recommended.
3. Install:
   ```bash
   pip install -r requirements.txt
