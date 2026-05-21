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
- 2026-04-27 10:09 — commit: Refresh: Update AI Hub for April 27, 2026 (curated news + render) | dashboards/AI-Discovery-Hub-2026-04-27.html,dashboards/latest.html,data/hub-input.json,data/hub-output.json,index.html
- 2026-04-27 10:31 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals
- 2026-04-27 10:48 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-27.html | 20 artifacts
- 2026-04-27 10:48 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-27 12:00 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-27 12:02 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-27.html | 20 artifacts
- 2026-04-27 12:02 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-27.html | 20 artifacts
- 2026-04-27 12:04 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-27 12:05 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-28 23:53 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals
- 2026-04-28 23:54 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-28.html | 20 artifacts
- 2026-04-29 00:01 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals
- 2026-04-29 00:02 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-29 00:02 — build_hub.py → completed | → AI-Discovery-Hub-2026-04-29.html | 20 artifacts
- 2026-04-29 00:02 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-29 00:16 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-04-29 11:19 — session ended | stop_reason: unknown | cwd: /Users/danielbally/Git/ai-discovery-hub
- 2026-05-01 21:18 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals
- 2026-05-01 21:19 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-01.html | 20 artifacts
- 2026-05-01 21:19 — commit: Refresh: Update AI Hub for May 1, 2026 (curated news + render) | dashboards/AI-Discovery-Hub-2026-05-01.html,dashboards/latest.html,data/hub-input.json,data/hub-output.json
- 2026-05-01 22:22 — fetch_feed.py → exited_unexpectedly
- 2026-05-02 20:43 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-02.html | 20 artifacts
- 2026-05-02 20:44 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-02.html | 20 artifacts
- 2026-05-04 17:40 — fetch_feed.py → exited_unexpectedly
- 2026-05-04 17:43 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals · 2 questions · 10 tutorials
- 2026-05-04 22:43 — fetch_feed.py → completed | 0 videos · 0 repos · 0 signals · 0 questions · 0 tutorials
- 2026-05-04 22:43 — build_hub.py → failed | Connection error.
- 2026-05-04 22:43 — build_hub.py → exited_unexpectedly
- 2026-05-04 22:46 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-04.html | 20 artifacts
- 2026-05-08 11:46 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals · 2 questions · 10 tutorials
- 2026-05-08 11:52 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-08.html | 20 artifacts
- 2026-05-08 11:52 — commit: Refresh: Update AI Hub for May 8, 2026 (curated news + render) | dashboards/AI-Discovery-Hub-2026-05-08.html,dashboards/latest.html,data/hub-input.json,data/hub-output.json
- 2026-05-13 11:27 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals · 1 questions · 10 tutorials
- 2026-05-13 11:28 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 20 artifacts
- 2026-05-13 11:28 — commit: Refresh: Update AI Hub for May 13, 2026 (curated news + render) | dashboards/AI-Discovery-Hub-2026-05-13.html,dashboards/latest.html,data/hub-input.json,data/hub-output.json

- 2026-05-13 11:28 — fetch_feed.py → completed | 10 videos · 15 repos · 10 signals · 1 questions · 10 tutorials
- 2026-05-13 11:28 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 20 artifacts
- 2026-05-13 11:28 — commit: Refresh: Update AI Hub for May 13, 2026 (curated news + render) | dashboards/AI-Discovery-Hub-2026-05-13.html,dashboards/latest.html,data/hub-input.json,data/hub-output.json
- 2026-05-13 12:41 — commit: fix: write hub descriptions in second person (you/your, not Daniel/he) | execution/prompts.py
- 2026-05-13 12:59 — expand_lab.py → completed | item 1: Wire the Claude Code Agent Dashboard into your FME debug loo
- 2026-05-13 13:01 — expand_lab.py → completed | item 2: Replicate the Sentinel-2 soil salinity workflow and adapt it
- 2026-05-13 13:04 — expand_lab.py → completed | item 3: Install everything-claude-code and benchmark it against your
- 2026-05-13 13:05 — expand_lab.py → completed | item 4: Add claude-mem persistence to your Sentinel Hub scripting se
- 2026-05-13 13:06 — expand_lab.py → completed | item 4: Add claude-mem persistence to your Sentinel Hub scripting se
- 2026-05-13 13:08 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 23 artifacts
- 2026-05-13 13:09 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 23 artifacts
- 2026-05-13 13:13 — expand_lab.py → completed | item 1: Wire the Claude Code Agent Dashboard into Your FME Automatio
- 2026-05-13 13:14 — expand_lab.py → completed | item 2: Add claude-mem Persistence to Your Sentinel Hub Scripting Se
- 2026-05-13 13:16 — expand_lab.py → completed | item 3: Replicate the Sentinel-2 Soil Salinity SVM Workflow and Laye
- 2026-05-13 13:18 — expand_lab.py → completed | item 4: Benchmark everything-claude-code Skills Module Against Your 
- 2026-05-13 13:20 — expand_lab.py → completed | item 5: Build a Statistical Prompt Evaluation Harness for Your Claud
- 2026-05-13 13:21 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 23 artifacts
- 2026-05-13 13:21 — commit: feat: generate lab curricula for May 13 exercises (5 tutorials linked) | curriculums/2026-04-22-apply-llm-eval-patterns-to-one-existing-claude-api-tool.md,curriculums/2026-04-22-apply-spec-driven-development-to-one-fme-workflow-with-claude-code.md,curriculums/2026-04-22-audit-your-claude-code-plan-document-current-usage.md,curriculums/2026-04-22-audit-your-claude-plan-and-document-cost-risk-exposure.md,curriculums/2026-04-22-build-a-minimal-claude-code-contingency-test-with-an-ollama-local-model.md
- 2026-05-13 14:56 — expand_lab.py → completed | item 1: Wire the Claude Code Agent Dashboard into Your FME Automatio
- 2026-05-13 14:58 — expand_lab.py → completed | item 2: Add claude-mem Persistence to Your Sentinel Hub Scripting Se
- 2026-05-13 15:00 — expand_lab.py → completed | item 3: Replicate the Sentinel-2 Soil Salinity SVM Workflow and Laye
- 2026-05-13 15:00 — build_hub.py → completed | → AI-Discovery-Hub-2026-05-13.html | 23 artifacts
- 2026-05-13 15:00 — commit: feat: ground lab tutorials in source content + add disclaimer banner | curriculums/2026-05-13-add-claude-mem-persistence-to-your-sentinel-hub-scripting-sessions.md,curriculums/2026-05-13-replicate-the-sentinel-2-soil-salinity-svm-workflow-and-layer-in-a-claude-assisted-classification-step.md,curriculums/2026-05-13-wire-the-claude-code-agent-dashboard-into-your-fme-automation-pipeline.md,dashboards/curricula/add-claude-mem-persistence-to-your-sentinel-hub-scripting-sessions.html,dashboards/curricula/benchmark-everything-claude-code-skills-module-against-your-current-claude-md-approach.html
- 2026-05-13 15:01 — expand_lab.py → completed | item 4: Benchmark everything-claude-code Skills Module Against Your 
- 2026-05-13 15:03 — expand_lab.py → completed | item 5: Build a Statistical Prompt Evaluation Harness for Your Claud
- 2026-05-17 09:29 — commit: feat: initialize project architecture with standardized AI directives, knowledge tracking, and execution modules. | AGENTS.md,CLAUDE.md,GEMINI.md,README.md,curriculums/2026-05-13-benchmark-everything-claude-code-skills-module-against-your-current-claude-md-approach.md
- 2026-05-17 09:33 — commit: docs: record project architecture initialization and standardized AI directives in SESSION.md | knowledge/SESSION.md
