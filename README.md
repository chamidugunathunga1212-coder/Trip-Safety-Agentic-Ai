# Trip-Safety-Agentic-Ai



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
