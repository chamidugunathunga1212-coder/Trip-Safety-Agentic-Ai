"""
agents.py

Contains:
- AgentBase: a simple agent class that uses OpenAI (and can be adapted to autogen v0.7)
- RiskAssessmentAgent
- AdvisoryAgent
- EmergencyAgent

Notes:
- The autogen usage is deliberately minimal here so you can plug autogen v0.7 orchestration
  quickly. Replace the LLM wrapper calls with autogen integrations if you want detailed
  agent choreography from autogen.
"""

import os
import time
from typing import Dict, Any, List
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

from nlp import extract_locations, extract_time, extract_transport_mode
from tools import fetch_weather_for_location, fetch_emergency_info_for_location
from utils import compute_risk_score, summarize_text

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- Generic Agent base ----------
class AgentBase:
    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt

    def _call_llm(self, prompt: str, temperature: float = 0.2, max_tokens: int = 400) -> str:
        """
        OpenAI chat completion wrapper for AgentBase.
        Returns a string reply or a safe error message.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # Safely get content
            if resp.choices and resp.choices[0].message and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip()
            else:
                return "No response from LLM."
        except Exception as e:
            print("LLM call failed:", e)
            return "LLM call failed."


# ---------- Risk Assessment Agent ----------
class RiskAssessmentAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="risk_assessment_agent",
            system_prompt=(
                "You are Risk Assessment Agent. Extract locations, transport modes, time of travel. "
                "Fetch weather and emergency info using the provided tools, and return a structured "
                "risk assessment (json) with reasons and recommended severity."
            ),
        )

    def handle(self, user_text: str) -> Dict[str, Any]:
        # 1. NLP extraction
        locations = extract_locations(user_text)
        times = extract_time(user_text)
        transport = extract_transport_mode(user_text)

        # fallback to at least one location
        if not locations:
            locations = ["unknown"]

        # 2. Call external retrieval (weather + emergency)
        weather_data = {}
        emergency_data = {}
        for loc in locations:
            weather_data[loc] = fetch_weather_for_location(loc)
            emergency_data[loc] = fetch_emergency_info_for_location(loc)

        # 3. Construct prompt for LLM to synthesize
        prompt = (
            f"User: {user_text}\n"
            f"Extracted locations: {locations}\n"
            f"Time: {times}\n"
            f"Transport: {transport}\n"
            f"Weather (raw): {weather_data}\n"
            f"Emergency intel (raw): {emergency_data}\n\n"
            "Produce:\n"
            "1) JSON object with fields: locations, time, transport_mode, risk_score (0-100), "
            "risk_level (Low/Medium/High/Critical), reasons (list), recommended_actions (list).\n"
            "2) Short human summary (1-2 paragraphs).\n"
        )
        llm_out = self._call_llm(prompt)
        # try to extract json inside output (best-effort)
        try:
            import json, re
            # find first JSON-looking block
            m = re.search(r"(\{.*\})", llm_out, re.S)
            if m:
                parsed = json.loads(m.group(1))
            else:
                parsed = {"raw_text": llm_out}
        except Exception:
            parsed = {"raw_text": llm_out}

        # 4. Compute deterministic supplemental score (example)
        supplemental_score = compute_risk_score(weather_data, emergency_data, transport)
        if "risk_score" in parsed and isinstance(parsed["risk_score"], (int, float)):
            parsed["risk_score_final"] = round((parsed["risk_score"] + supplemental_score) / 2)
        else:
            parsed["risk_score_final"] = supplemental_score

        parsed["weather_data"] = weather_data
        parsed["emergency_data"] = emergency_data
        parsed["summary"] = summarize_text(llm_out, max_sentences=3)
        parsed["agent"] = self.name
        return parsed

# ---------- Advisory Agent ----------
class AdvisoryAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="advisory_agent",
            system_prompt=(
                "You are Advisory Agent. Given a risk assessment (structured JSON), produce "
                "tailored, practical advice for the user: packing, timing, alternate routes, "
                "how to reduce risk, and short checklist items."
            ),
        )

    def handle(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"Risk assessment JSON:\n{assessment}\n\n"
            "Produce:\n"
            "1) A friendly advisory message (3-6 bullet points)\n"
            "2) A short checklist of items to carry (e.g., medications, charger, documents)\n"
            "3) Accessibility / special-needs considerations if any\n"
        )
        advice = self._call_llm(prompt)
        return {"agent": self.name, "advice_text": advice, "original_assessment": assessment}

# ---------- Emergency Agent ----------
class EmergencyAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="emergency_agent",
            system_prompt=(
                "You are Emergency Agent. When risk is high or emergency is detected, provide contact "
                "info, immediate steps, and how to call local services. If the assessment has actionable "
                "emergency info, structure it clearly."
            ),
        )

    def handle(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        # For each location return emergency contacts and next steps
        prompt = (
            f"Assessment:\n{assessment}\n\n"
            "Return in JSON: locations -> list of {location, emergency_contacts, next_steps, 3-min response checklist}\n"
        )
        resp = self._call_llm(prompt)
        try:
            import json, re
            m = re.search(r"(\{.*\})", resp, re.S)
            if m:
                parsed = json.loads(m.group(1))
            else:
                parsed = {"raw_text": resp}
        except Exception:
            parsed = {"raw_text": resp}
        return {"agent": self.name, "emergency_plan": parsed, "raw": resp}
