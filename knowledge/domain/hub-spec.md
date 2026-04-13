# AI Discovery Hub — Dashboard Specification

The AI Discovery Hub is a unified, reference-grade dashboard that consolidates agentic tool discovery (Repos), social market signals (Reddit/Substack), and deep-dive technical research (YouTube Briefings).

## 1. Design Philosophy
- **Tufte-Inspired**: High data density, minimal UI chrome, color used only to convey meaning.
- **Glassmorphic**: Subtle translucency for cards and panels.
- **Unified Feed**: Tools, Videos, and Articles live in the same grid but are clearly typed.
- **Dependency-Free**: Pure HTML/CSS/JS. No frameworks. One file per report.

## 2. Color Palette
| Token | Hex | Use |
| :--- | :--- | :--- |
| `--bg` | `#080b12` | Main page background |
| `--bg2` | `#0e1220` | Panel background |
| `--bg3` | `#151c2e` | Card background (subtle glass) |
| `--border` | `#252e4a` | Standard divider |
| `--blue` | `#5b8af7` | Current / Monitoring |
| `--green` | `#34d89a` | Actionable / Adopt |
| `--orange` | `#f97c3c` | Multi-Agent / High Signal |
| `--purple` | `#7c5cfc` | Research / Architecture |
| `--pink` | `#f05d9a` | Hype / Warning |
| `--yellow` | `#f5c842` | Foundation / Home |

## 3. Unified Taxonomy (Strict)

Every "Artifact" (Card) MUST have:
1.  **1 Lens** (Context)
2.  **1 Tier** (Priority)
3.  **1-2 Topics** (Subject)

### Lenses (Audience)
- `t-home`: 🏠 Home Hobbyist (Personal automation, local tools)
- `t-curr`: 📡 Staying Current (AI/Model news, platform updates)
- `t-gis`: 🗺 GIS/FME (Geospatial AI, FME automation, satellite, spatial data pipelines)

### Tiers (Priority)
- `t-adopt`: ✅ Adopt Now (High ROI, stable, integrated)
- `t-watch`: 👁 Watch Closely (Rising signal, trending, potential)
- `t-hype`: 🔥 Hype Check (Viral, needs validation, contested)
- `t-found`: 🧱 Foundation (Essential infrastructure/concepts)

### Topics (Subjects)
- `t-claude`: Claude Code & CLI
- `t-agent`: Multi-Agent Orchestration
- `t-local`: Local Inference (Ollama, local LLMs)
- `t-mcp`: MCP Servers & Protocol
- `t-data`: Data Prep & Pipelines
- `t-voice`: Voice / Speech AI
- `t-memory`: AI Memory/RAG
- `t-model`: Model Releases / Papers
- `t-budget`: Budget & Finance AI
- `t-fme`: FME / ETL (Safe Software, spatial data transformation, data integration)
- `t-geoai`: GeoAI (LLMs + GIS, computer vision on satellite/aerial imagery, spatial ML)

## 4. Components

### Artifact Card (Hybrid)
A unified card structure that adapts based on its `type`:
```
[artifact-icon]        ← 20px emoji or SVG
[title]                ← 12.5px bold
[meta-row]             ← Channel | Slug | Domain (9.5px mono)
[social-signal]        ← Trending #N | Reddit | Substack (italic, 10px)
[description]          ← 2-3 sentences max (11px)
[tag-row]              ← [Lens] [Tier] [Topic]
```

### Top Activity Heatmap
Combines **YouTube uploads** (blue dots) and **Repo updates/Social hits** (orange dots) for a unified channel pulse.

### Model Tracker
Notable model releases, papers, or framework updates from the week.

### The Lab (Exercises)
Actionable walkthroughs or experiments to run, prioritized by effort (Low/Med/High).

## 5. Logic & Features

### Default Sort: Tier-Priority
Cards are grouped by Tier in the HTML structure:
1. ✅ Adopt Now
2. 👁 Watch Closely
3. 🔥 Hype Check
4. 🧱 Foundation

### Feature: Recency Sorting
A `<script>` included in every dashboard allows the user to toggle `Sort by: Priority (default)` vs `Sort by: Recency`.
- The JS reads the `data-date` attribute on each card and re-sorts the DOM elements.

### Metadata Footer
Shows the generation date, total signals monitored, and the **AI Model Backend** used (e.g., "Powered by Claude 3.5 Sonnet").
