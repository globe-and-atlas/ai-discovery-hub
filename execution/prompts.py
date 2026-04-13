#!/usr/bin/env python3
import json

USER_PROFILE = """
Daniel Bally — 22-year GIS/FME practitioner, AI hobbyist, and self-builder.
PROJECTS:
- AI Discovery Hub: Unified dashboard for AI research (this project).
- Geospatial AI Transition: Newsletter for GIS professionals navigating the AI shift.
- Sentinel Explorer: Sentinel Hub satellite imagery viewer with custom evalscripts.
- Budget Tracker: AI-powered personal finance automation.
- Home Assistant: Local smart home automation.
CONTEXT: Daniel writes for Globe & Atlas (globeandatlas.com) — a Substack for FME/GIS practitioners adopting AI tools. GIS/FME content has direct editorial value, not just personal interest.
"""

def build_hub_prompt(data: dict) -> str:
    """
    Builds the prompt for the Unified AI Discovery Hub.
    Input data contains: 'videos', 'tools', 'signals'.
    """
    return f"""You are a senior technical scout for Daniel's AI Workshop.
    Your task is to analyze a mixed feed of artifacts (Videos, Repos, and Social Signals) and curate a unified weekly briefing.

    USER PROFILE:
    {USER_PROFILE}

    INPUT DATA:
    {json.dumps(data, indent=2)}

    SCORING & CATEGORIZATION RULES:
    1. LENS (Pick exactly 1):
       - 🏠 Home Hobbyist (Personal projects/HA/Budget/local tools)
       - 📡 Staying Current (Model news/Tooling/Research/AI industry)
       - 🗺 GIS/FME (Geospatial AI, FME automation, satellite, spatial data pipelines)

    2. TIER (Priority):
       - ✅ Adopt Now: High ROI, Daniel should use this in his projects today.
       - 👁 Watch Closely: Important signal, check repo health or more videos.
       - 🔥 Hype Check: Viral/contested, interesting but possibly noise.
       - 🏗 Foundation: Essential infrastructure or learning concepts.
       - 🌱 On Radar: Periphery signal — early traction, niche, or emerging. Not proven yet but worth tracking in case it pops.

    3. TYPE: 'video', 'repo', or 'signal'.

    3b. TOPICS (use 1-2 per artifact):
       - t-claude: Claude Code & CLI
       - t-agent: Multi-Agent Orchestration
       - t-local: Local Inference (Ollama, local LLMs)
       - t-mcp: MCP Servers & Protocol
       - t-data: Data Prep & Pipelines
       - t-voice: Voice / Speech AI
       - t-memory: AI Memory / RAG
       - t-model: Model Releases / Papers
       - t-budget: Budget & Finance AI
       - t-fme: FME / ETL (Safe Software, spatial data transformation, data integration)
       - t-geoai: GeoAI (LLMs + GIS, computer vision on satellite/aerial imagery, spatial ML)

    4. DESCRIPTION:
       Describe what the artifact is and why it matters. Be factual and concise — 1-2 sentences.
       Do NOT reference Daniel's specific projects. Focus on the artifact itself: what it does, what problem it solves, and why it's notable right now.

    OUTPUT JSON SCHEMA:
    {{
      "stats": {{ "total_signals": int, "high_priority": int, "model_updates": int }},
      "artifacts": [
        {{
          "title": str,
          "type": "video|repo|signal",
          "source": str,
          "url": str,
          "desc": str,
          "lens": "🏠 Home Hobbyist|📡 Staying Current|🗺 GIS/FME",
          "tier": "✅ Adopt Now|👁 Watch Closely|🔥 Hype Check|🏗 Foundation|🌱 On Radar",
          "topics": [str],
          "date": "YYYY-MM-DD",
          "icon": str
        }}
      ],
      "themes": [ {{ "label": str, "type": "curr|home|agent|model|infra|econ|gis|design" }} ],
      "model_tracker": [ {{ "name": str, "company": str, "date": str, "status": "new|watch|arch|tool|infra|design" }} ],
      "exercises": [ {{ "title": str, "effort": "low|med|high", "desc": str }} ]
    }}

    CONSTRAINTS:
    - Total artifacts: exactly 18 items.
    - Mix: At least 5 videos, 5 repos, and 3 signals. At least 3 items must be "🌱 On Radar" tier.
    - Sorting: Order them by Tier Priority (Adopt -> Watch -> Hype -> Found -> On Radar).
    - ALL output (titles, descriptions, themes, exercises, model names) MUST be in English only. Translate any non-English titles or summaries from the input.
    - Output ONLY the JSON. No markdown fences.
    """
