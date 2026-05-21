# AI Discovery Hub

A personal signal-intelligence pipeline for staying current with AI and geospatial tooling. It fetches content from five public sources, runs it through an LLM curation pass, and produces a self-contained HTML dashboard ranking each item by relevance to a defined personal stack.

A new dashboard is generated on a schedule. Each report is a single static HTML file — no server, no dependencies, no login.

---

## What it does

1. **Fetches** raw content from YouTube, GitHub, Reddit, GIS Stack Exchange, and Dev.to
2. **Filters** with an LLM against a personal stack profile — items are scored as `personal`, `adjacent`, or `world`
3. **Classifies** surviving items into Lenses (who cares), Tiers (how urgent), and Topics (what it's about)
4. **Generates** actionable lab exercises for every top-tier item
5. **Renders** a single static HTML dashboard with all of the above

---

## Sources

All source configuration lives in `execution/fetch_feed.py`. Each source is a named constant at the top of the file — no config files, no environment variables needed for the fetch step itself.

### YouTube

Two sweep types run in sequence:

**Channel uploads** — a hardcoded list of channels checked for new videos in the lookback window:

| Channel | Focus |
|---|---|
| Fireship | AI dev tools, short-form tutorials |
| Andrej Karpathy | LLM research and pedagogy |
| Two Minute Papers | Academic AI paper summaries |
| Yannic Kilcher | ML paper deep-dives |
| Computerphile | CS fundamentals and concepts |
| sentdex | Python and ML tutorials |
| Dot CSV | Spanish-language AI (translated signal) |
| Veritasium | Science and engineering explainers |
| Safe Software | FME and spatial ETL |
| QGIS | Open-source GIS |
| Esri / Esri Events | ArcGIS and enterprise GIS |
| Sentinel Hub | Satellite imagery APIs |
| Planet Labs | Commercial satellite data |
| Maxar Technologies | High-resolution imagery |
| Google Earth | Earth Engine and geospatial tools |

**Keyword search** — 16 queries run against YouTube Search covering Claude Code, Gemini, local LLM inference, geospatial AI, FME, QGIS, satellite imagery, drone analysis, and Sentinel-2.

**To add or remove a channel:** edit `YOUTUBE_CHANNELS` in `fetch_feed.py` — each entry is a `(channel_id, display_name)` tuple. The channel ID is the `UC...` string from the channel's URL.

**To add or remove a search query:** edit `YOUTUBE_SEARCH_QUERIES`. Each string is passed directly to YouTube's search API.

**Requires:** `YOUTUBE_API_KEY` or `GOOGLE_API_KEY` in `.env` (YouTube Data API v3). Without a key, YouTube is silently skipped.

---

### GitHub

Searches repositories by topic using the GitHub REST API. A `stars:>10` filter and a `pushed:>[since_date]` filter drop abandoned or low-traction repos before they reach the LLM.

Current topics monitored:

```
# LLM / AI tooling
llm, ai-agent, mcp-server, local-llm, claude, openai, gemini,
langchain, ollama, anthropic

# GIS / Geospatial
geospatial-ai, geoai, qgis, geemap, sentinel-hub, spatial-data,
arcgis, esri, fme, remote-sensing

# Imagery / Sensing
satellite-imagery, multispectral, hyperspectral, sar,
drone, uav, thermal-imaging, change-detection
```

**To add or remove topics:** edit `GITHUB_TOPICS` in `fetch_feed.py`.

**Auth:** `GITHUB_TOKEN` in `.env` raises the rate limit from 60 to 5000 requests/hour. The fetcher works without it but may hit rate limits on dense runs.

---

### Reddit

Scrapes the `hot` feed of specific subreddits using Reddit's public `.json` endpoints — no API key or OAuth required.

Current subreddits:

```
MachineLearning, LocalLLaMA, artificial, ClaudeAI, ChatGPT, Bard,
singularity, gis, remotesensing, geospatial
```

Posts with a score below 50 and stickied mod posts are dropped before the LLM sees them. The fetcher polls public JSON endpoints (`reddit.com/r/{sub}/hot.json`) with a polite 0.5s delay between requests.

**To add or remove subreddits:** edit `REDDIT_SUBREDDITS` in `fetch_feed.py`.

**No auth required.** The fetcher identifies itself with a `User-Agent` header per Reddit's API guidelines.

---

### GIS Stack Exchange

Fetches recent questions from `gis.stackexchange.com` filtered by tag combinations using the public Stack Exchange API.

Current tag sets monitored:

```
machine-learning, artificial-intelligence, python,
qgis+python, fme-desktop, remote-sensing, satellite-imagery
```

**To add or remove tags:** edit `STACKEXCHANGE_TAG_SETS` in `fetch_feed.py`. Use `+` to combine tags (AND logic).

**Auth:** `STACKAPPS_KEY` in `.env` raises the rate limit from 300 to 10,000 requests/day. Not required for normal operation.

---

### Dev.to

Fetches recent practitioner articles filtered by tag using the public Dev.to API.

Current tags:

```
gis, machinelearning, artificialintelligence,
python, satellite, geospatial
```

**To add or remove tags:** edit `DEVTO_TAGS` in `fetch_feed.py`.

**No auth required.**

---

### What's not yet implemented

The dashboard spec references **Substack newsletters** as a planned signal source alongside Reddit. Substack's public RSS feeds (`{publication}.substack.com/feed`) are machine-readable and could be added with a straightforward RSS fetcher — but this is not currently wired into `fetch_feed.py`. Adding it would follow the same pattern as Dev.to: a list of feed URLs at the top of the file, a fetch function, and an entry in the output JSON.

---

## LLM curation pass

After fetching, `build_hub.py` sends the raw content to Claude along with a `STACK_PROFILE` — a description of the personal toolchain (Python, React, Vite, Claude API, FME, QGIS, Sentinel Hub) and an explicit `NOT RELEVANT` list (iOS/Android, Java, Rust, gaming engines, Web3).

The LLM scores each item:

- **`personal`** — directly relevant to the stack or a 1-step adjacent upgrade
- **`world`** — acknowledged but demoted to the bottom "AI World at Large" section, excluded from analytics and Lab exercises

Surviving `personal` items are classified with:

| Dimension | Values |
|---|---|
| **Lens** (audience) | 🏠 Home Hobbyist · 📡 Staying Current · 🗺 GIS/FME |
| **Tier** (urgency) | ✅ Adopt Now · 👁 Watch Closely · 🔥 Hype Check · 🧱 Foundation · 🌱 On Radar |
| **Topic** (subject) | Claude Code · Multi-Agent · Local LLM · MCP · FME/ETL · GeoAI · etc. |

Every `Adopt Now` item gets a Lab exercise — a concrete, effort-labelled action (Low / Med / High) linking back to the source.

**To change what's relevant to you:** edit the `STACK_PROFILE` and `NOT_RELEVANT` sections in `execution/prompts.py`.

---

## Run the pipeline

```bash
# 1. Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Copy and fill in API keys
cp .env.example .env   # then add YOUTUBE_API_KEY, ANTHROPIC_API_KEY

# 3. Fetch sources → data/hub-input.json
python3 execution/fetch_feed.py

# 4. Curate and render → dashboards/latest.html
python3 execution/build_hub.py

# 5. Open the dashboard
open dashboards/latest.html
```

**Widen the lookback window:**

```bash
python3 execution/fetch_feed.py --days 14 --max-videos 20 --max-repos 25
```

**Dry run (no writes):**

```bash
python3 execution/fetch_feed.py --dry-run
```

---

## Required API keys

| Key | Source | Required? |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Yes — powers the curation pass |
| `YOUTUBE_API_KEY` | Google Cloud Console (YouTube Data API v3) | Yes for YouTube; other sources still run without it |
| `GITHUB_TOKEN` | github.com/settings/tokens | No — but raises rate limit from 60 to 5000 req/hr |
| `STACKAPPS_KEY` | stackapps.com | No — raises Stack Exchange limit from 300 to 10k req/day |

---

## Project structure

```
execution/
  fetch_feed.py      # Source fetcher — all source config lives here
  build_hub.py       # LLM curation pass and HTML rendering
  prompts.py         # System prompt, stack profile, not-relevant list
  kb.py              # Knowledge base logging utilities

data/
  hub-input.json     # Raw feed output (overwritten each run)
  hub-output.json    # Curated LLM output (overwritten each run)

dashboards/
  latest.html        # Symlink or copy of the most recent report
  AI-Discovery-Hub-YYYY-MM-DD.html   # Dated archive of past reports

knowledge/
  domain/hub-spec.md          # Dashboard taxonomy and design spec
  domain/api_constraints.md   # Known API limits and quirks
  procedural/run_pipeline.md  # Step-by-step run instructions
```
