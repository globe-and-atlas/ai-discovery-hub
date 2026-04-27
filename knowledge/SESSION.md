# SESSION — AI Discovery Hub

## Last Known State

**Date:** 2026-04-23
**Status:** Operational. Full pipeline running. All 4 lab curricula generated and linked.

### What's working
- `fetch_feed.py` — YouTube (10), GitHub (15), Reddit (10) all pulling cleanly
- `build_hub.py` — LLM generation + HTML render working
- `expand_lab.py` — Sequential curriculum generation with 529 retry backoff
- `build_hub.py --render-only` — Re-render from cached hub-output.json
- Curriculum linking — `curriculum_path` written to hub-output.json, survives title rewrites
- Standalone curriculum HTML pages at `dashboards/curricula/`

### Known limitations
- GitHub token expires periodically — regenerate at github.com/settings/tokens
- Anthropic API 529s during peak load — sequential expand_lab calls + retry logic in place
- Exercise titles rewrite on every full build — mitigated by curriculum_path in hub-output.json

### Sources monitored
- YouTube: 16 channels (AI/dev + GIS/FME/Esri + satellite/imagery)
- GitHub topics: 28 topics (LLM/AI + GIS/geospatial + satellite/drone/thermal imagery)
- Reddit: 10 subreddits (ML, LocalLLaMA, ClaudeAI, ChatGPT, gis, remotesensing, geospatial, etc.)

---

## Checkpoint Log

### 2026-04-22 — Initial pipeline build
- Built fetch_feed.py, build_hub.py, expand_lab.py, prompts.py
- Dashboard rendering with dark theme, filters, tier system
- Curriculum pages: generated as inline collapsible → upgraded to standalone HTML pages

### 2026-04-22 — Curriculum linking
- Fixed: duplicate GITHUB_TOKEN in .env causing 401
- Built: expand_lab.py generates curricula, build_hub.py links them
- Bug discovered: title drift breaks slug matching on every full rebuild
- Fix: curriculum_path written to hub-output.json by expand_lab.py

### 2026-04-23 — Feed expansion + error hardening
- Added: Esri, ChatGPT/OpenAI, Gemini/Google AI to stack profile and topics
- Added: satellite, drone, thermal, multispectral imagery sources and GitHub topics
- Added: 6 new YouTube channels (Esri, Sentinel Hub, Planet, Maxar, Google Earth)
- Added: 529 retry backoff to expand_lab.py
- Added: --render-only flag to build_hub.py
- Created: knowledge/ system (ERRORS.md, SESSION.md, INDEX.md, domain/, procedural/)
- 2026-04-24 22:19 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-26 15:39 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-26 15:40 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-27 09:58 — fetch_feed.py → completed | 0 videos · 0 repos · 0 signals
- 2026-04-27 09:59 — build_hub.py → failed | Connection error.
- 2026-04-27 09:59 — build_hub.py → exited_unexpectedly
- 2026-04-27 10:04 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-27.html | 5 artifacts
- 2026-04-27 10:08 — build_hub.py → exited_unexpectedly
- 2026-04-27 10:08 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-27.html | 5 artifacts
