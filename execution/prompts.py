#!/usr/bin/env python3
import json

# Stack profile derived from CLAUDE.md stack table + project inventory
STACK_PROFILE = """
STACK (direct):
- Languages: Python 3, TypeScript, JavaScript
- Python libs: Streamlit, python-dotenv, pathlib, pdfplumber, Playwright, requests, rasterio, geopandas, GDAL
- Frontend: React 19, Vite, TypeScript
- AI/LLM: Claude API (Anthropic), claude-sonnet-4-6, claude-haiku-4-5, Anthropic SDK
- GIS/Geospatial: FME (Safe Software), Sentinel Hub API, QGIS, ArcGIS Pro, WMS/WMTS, H3, GeoJSON
- Deployment: Vercel, GitHub Actions, GitHub Pages
- Data: JSON, PDF parsing, REST APIs, YouTube Data API, GitHub API, Reddit API
- Dev tools: Claude Code CLI, VS Code, tmux, git, zsh

ADJACENT (one step away — tools that could replace or significantly enhance direct stack items):
- Any Python library that replaces or meaningfully upgrades something above
- Any LLM model or API that competes with or extends Claude API usage
- Any geospatial AI tool that works with or replaces FME/Sentinel Hub/QGIS workflows
- Any frontend framework evolution affecting React 19 + Vite
- Any agent orchestration tool relevant to the 3-layer architecture (directives/orchestration/execution)
- Any deployment tooling that affects Vercel or GitHub Actions workflows

NOT RELEVANT (filter to world section):
- Mobile development, iOS, Android
- Java, C++, Rust, Go (unless replacing a Python tool)
- Gaming engines, Unity, Unreal
- Blockchain, crypto, Web3
- Enterprise SaaS platforms (Salesforce, SAP, etc.)
- Tools with no clear connection to Python, GIS, LLMs, or React
"""

USER_CONTEXT = """
Daniel Bally — 22-year GIS/FME practitioner transitioning to AI-augmented workflows.
Publishes Globe & Atlas (Substack) — practitioner-level content for GIS professionals adopting AI.
Four editorial pillars: The Build (hands-on FME/AI workflows), Tool Critic (honest reviews),
Career Navigator (AI transition guidance), Industry Lens (signal vs noise analysis).
GIS/FME/Sentinel content has direct editorial value beyond personal interest.
"""

def build_hub_prompt(data: dict) -> str:
    return f"""You are a senior technical scout for Daniel's AI Workshop.
Analyze a mixed feed of artifacts (Videos, Repos, Social Signals) and produce a structured weekly briefing.

USER CONTEXT:
{USER_CONTEXT}

STACK PROFILE:
{STACK_PROFILE}

INPUT DATA:
{json.dumps(data, indent=2)}

SCORING RULES:

1. RELEVANCE (Pick exactly 1):
   - "personal": Directly touches Daniel's stack OR is adjacent (one step away with clear upgrade/replacement value).
     For adjacent items, relevance_why must explain the specific connection to his stack.
   - "world": Notable AI development that doesn't connect to his stack. Awareness only.

2. LENS (Pick exactly 1 — for personal items only, set "world" items to "📡 AI World"):
   - 🏠 Home Hobbyist: Personal projects, local tools, home automation, budgeting
   - 📡 Staying Current: Claude API, model releases, AI industry, agent tooling, Anthropic
   - 🗺 GIS/FME: Geospatial AI, FME automation, Sentinel Hub, satellite imagery, spatial data

3. TIER (Pick exactly 1):
   - ✅ Adopt Now: High ROI — ready to use in Daniel's projects today
   - 👁 Watch Closely: Important signal — evaluate soon, not quite ready to act
   - 🔥 Hype Check: Viral or contested — interesting but possibly noise
   - 🏗 Foundation: Core infrastructure or concept — worth understanding
   - 🌱 On Radar: Early traction — not proven yet, but track if it gains momentum

4. TYPE: "video", "repo", or "signal"

5. TOPICS (1-2 per artifact):
   - t-claude: Claude Code & CLI
   - t-agent: Multi-Agent Orchestration
   - t-local: Local Inference (Ollama, local LLMs)
   - t-mcp: MCP Servers & Protocol
   - t-data: Data Prep & Pipelines
   - t-voice: Voice / Speech AI
   - t-memory: AI Memory / RAG
   - t-model: Model Releases / Papers
   - t-fme: FME / ETL (Safe Software, spatial data transformation)
   - t-geoai: GeoAI (LLMs + GIS, computer vision on satellite/aerial imagery, spatial ML)

6. DESCRIPTION:
   For personal items: 1-2 sentences on what it is and why it matters to Daniel's stack specifically.
   For world items: 1 sentence factual summary only. No stack references.

OUTPUT JSON SCHEMA:
{{
  "stats": {{ "total_signals": int, "personal_count": int, "world_count": int }},
  "artifacts": [
    {{
      "title": str,
      "type": "video|repo|signal",
      "source": str,
      "url": str,
      "desc": str,
      "relevance": "personal|world",
      "relevance_why": str,  // For personal items: "Direct: uses Python/Claude API" or "Adjacent: replaces X in your stack because Y". Empty string for world items.
      "lens": "🏠 Home Hobbyist|📡 Staying Current|🗺 GIS/FME|📡 AI World",
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
- Total artifacts: exactly 20 items.
- At least 12 must be "personal" relevance. Remainder are "world".
- Personal mix: at least 4 videos, 4 repos, 2 signals.
- At least 3 personal items must be "adjacent" (not direct stack match) — each must have a specific relevance_why.
- At least 3 items must be "🌱 On Radar" tier.
- exercises: 3 items, all referencing personal-relevance artifacts only.
- Sort order: personal items first (by tier: Adopt → Watch → Hype → Foundation → Radar), then world items.
- ALL output must be in English. Translate any non-English titles or summaries.
- Output ONLY valid JSON. No markdown fences.
"""
