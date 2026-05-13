# Build a 'Claude Code Second Brain' Context Architecture for GIS/FME Projects

## A Complete Curriculum for Structuring Persistent AI Context in Streamlit + Claude API Apps

---

## 1. Introduction & Context

### What Is This?

When you work with Claude Code or the Claude API across multiple sessions, Claude starts every conversation fresh — it has no memory of your project structure, your coding conventions, your FME workspace patterns, or the decisions you've already made. This is the **context problem**, and it silently kills productivity.

Ryan Wiggins (VP Product at Mercury) popularized a practical solution: the **"Second Brain" pattern** — a structured, persistent context file (typically `CLAUDE.md`) that lives in your project root and is automatically loaded by Claude Code at the start of every session. Think of it as a README that's written *for the AI*, not for humans.

This tutorial takes Wiggins' framework from the Peter Yang video and adapts it specifically for:
- **GIS and FME project types** (spatial data pipelines, coordinate systems, feature types)
- **Streamlit + Claude API apps** (your active stack)
- **3-layer agent architecture** (Directive → Orchestration → Execution)

### Why This Matters

| Without CLAUDE.md | With CLAUDE.md |
|---|---|
| Re-explaining your stack every session | Claude knows your stack instantly |
| Inconsistent code style across sessions | Enforced conventions automatically |
| Claude suggests wrong FME transformers | Claude knows your preferred transformer patterns |
| Losing context on architectural decisions | Decisions are logged and respected |
| Repetitive onboarding for every task | True "second brain" — persistent intelligence |

### The Ryan Wiggins Framework (Summarized)

Wiggins structures persistent context across **four zones**:

1. **Project Identity** — What this project is, who it's for, what problem it solves
2. **Technical Stack & Conventions** — Languages, frameworks, patterns, style rules
3. **Architecture Map** — How components connect, data flows, layer responsibilities
4. **Active State** — Current sprint goals, known issues, recent decisions, TODOs

This tutorial teaches you to implement all four zones, then publish a reusable template as a Build post on Globe & Atlas.

---

## 2. Prerequisites

### Knowledge Requirements

- [ ] Basic familiarity with Claude Code CLI (`claude` command in terminal) **or** the Claude API via Python
- [ ] Working knowledge of Streamlit app structure
- [ ] Understanding of FME workspaces and basic transformer vocabulary (Reader, Writer, FeatureMerger, etc.)
- [ ] Comfortable editing Markdown files
- [ ] Basic Git workflow (you'll be version-controlling your `CLAUDE.md`)

### Tools Required

```bash
# Verify Claude Code CLI is installed
claude --version

# Verify Python environment
python --version  # 3.10+ recommended

# Verify Streamlit
streamlit --version

# Verify you have a project directory to work in
ls ~/projects/  # or wherever your GIS/Streamlit projects live
```

### Accounts & Access

- [ ] Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)
- [ ] A Globe & Atlas account with posting privileges
- [ ] A GitHub repo (or local Git repo) for your target project

### Recommended: Watch First

Before starting the exercises, watch the Peter Yang / Ryan Wiggins video:
📺 [How to Build for AI Agents and a Claude Code Second Brain in 25 Min](https://www.youtube.com/watch?v=KzqpK1uCczw)

Focus on:
- **0:00–8:00** — The context problem and why CLAUDE.md exists
- **8:00–16:00** — Wiggins' four-zone structure
- **16:00–25:00** — Live demo of agent interaction with persistent context

---

## 3. Step-by-Step Guide

### Overview of Steps

```
Step 1: Audit Your Current Project Context
Step 2: Create the Base CLAUDE.md Structure
Step 3: Populate Zone 1 — Project Identity
Step 4: Populate Zone 2 — Technical Stack & Conventions
Step 5: Populate Zone 3 — Architecture Map (3-Layer Agent)
Step 6: Populate Zone 4 — Active State & Decision Log
Step 7: Add GIS/FME-Specific Context Blocks
Step 8: Test Your CLAUDE.md with Claude Code
Step 9: Templatize It for Reuse
Step 10: Publish as a Build Post on Globe & Atlas
```

---

### Step 1: Audit Your Current Project Context

Before writing a single line of `CLAUDE.md`, spend 10 minutes answering these questions about your target project. Open a scratch file and write raw notes.

```markdown
## My Project Audit (Scratch Notes)

**Project name:** _______________
**What does it do in one sentence?** _______________
**Who uses it?** _______________

**Core files I always touch:**
- _______________
- _______________

**Things Claude always gets wrong about this project:**
- _______________
- _______________

**FME specifics (if applicable):**
- Coordinate systems I work with: _______________
- Typical Reader/Writer formats: _______________
- Transformers I use constantly: _______________
- Transformers I NEVER want suggested: _______________

**Streamlit specifics:**
- State management approach: _______________
- How I structure pages: _______________
- Claude API call patterns I use: _______________

**Architectural decisions already made:**
- _______________
- _______________
```

**Why this step matters:** The audit prevents you from writing a generic CLAUDE.md. The most valuable context is the stuff Claude *gets wrong by default* — that's what needs to be explicitly stated.

---

### Step 2: Create the Base CLAUDE.md Structure

Navigate to your project root and create the file:

```bash
cd ~/projects/your-gis-project
touch CLAUDE.md
```

Paste this scaffold — it's the skeleton you'll fill in across Steps 3–7:

```markdown
# CLAUDE.md — [Project Name] Second Brain

> **For Claude:** Read this entire file before responding to any request in this
> project. This is your persistent context. Treat it as ground truth about
> this codebase, its conventions, and its current state.

---

## ZONE 1: PROJECT IDENTITY
<!-- What this is, who it's for, what problem it solves -->

## ZONE 2: TECHNICAL STACK & CONVENTIONS
<!-- Languages, frameworks, libraries, style rules -->

## ZONE 3: ARCHITECTURE MAP
<!-- Component relationships, data flows, layer responsibilities -->

## ZONE 4: ACTIVE STATE
<!-- Current goals, known issues, recent decisions, next TODOs -->

## ZONE 5: GIS/FME CONTEXT
<!-- Spatial data specifics, FME patterns, coordinate systems -->

---
*Last updated: [DATE] | Owner: [YOUR NAME]*
```

```bash
# Add to git immediately — context files should be version controlled
git add CLAUDE.md
git commit -m "chore: initialize CLAUDE.md second brain scaffold"
```

---

### Step 3: Populate Zone 1 — Project Identity

Zone 1 answers the question: *"What is this, really?"* Be specific. Claude's generic knowledge is broad but shallow — your domain knowledge here is what makes it useful.

```markdown
## ZONE 1: PROJECT IDENTITY

### Project Name
GIS Pipeline Dashboard — FME + Streamlit Integration Layer

### One-Line Purpose
A Streamlit app that triggers FME workspaces via the FME Server REST API,
monitors pipeline run status, and displays geospatial output on an
interactive map.

### Primary Users
- GIS analysts who are not Python developers
- Operations team running nightly data loads
- Daniel (developer/maintainer)

### Core Problem Being Solved
Manual FME workspace execution is error-prone and requires FME Workbench
access. This app provides a no-code interface for controlled pipeline
execution with audit logging.

### What Success Looks Like
- Analyst clicks "Run Pipeline" → FME job submits → status polls automatically
  → map updates with new data → run logged to PostGIS audit table
- Zero FME Workbench required for standard operations
- Sub-30-second status feedback on all pipeline runs

### What This Project Is NOT
- Not a replacement for FME Workbench for workspace development
- Not a general-purpose GIS viewer
- Not multi-tenant (single organization only)
```

---

### Step 4: Populate Zone 2 — Technical Stack & Conventions

This is where you prevent the most common Claude mistakes. Be opinionated. List what you *don't* want as much as what you do.

```markdown
## ZONE 2: TECHNICAL STACK & CONVENTIONS

### Core Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Streamlit | 1.32+ |
| AI/LLM | Anthropic Claude API | claude-3-5-sonnet-20241022 |
| GIS Display | Folium (via streamlit-folium) | 0.18+ |
| Data | GeoPandas, Shapely | 0.14+, 2.0+ |
| FME Interface | FME Server REST API (requests) | FME 2023.x |
| Database | PostGIS via psycopg2 | PostgreSQL 15 |
| Environment | python-dotenv | - |

### Python Conventions

**ALWAYS:**
- Use type hints on all function signatures
- Use `pathlib.Path` instead of `os.path`
- Use `logging` module (not `print`) for operational messages
- Prefix Streamlit session state keys with the page name: `map_page_layer_visible`
- Handle CRS explicitly — never assume a coordinate system

**NEVER:**
- Use `st.experimental_*` APIs (deprecated)
- Use bare `except:` clauses — always catch specific exceptions
- Store credentials in code — use `st.secrets` or `.env` via dotenv
- Use `geopandas.read_file()` without explicitly setting `engine="pyogrio"`

### Claude API Usage Pattern
```python
# THIS is the approved pattern for Claude API calls in this project
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def call_claude(system_prompt: str, user_message: str) -> str:
    """Standard Claude API call wrapper for this project."""
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text
```

**DO NOT** use streaming unless explicitly asked. **DO NOT** change the model
without updating this file.

### File & Folder Naming
```
project_root/
├── CLAUDE.md              ← You are here
├── app.py                 ← Streamlit entry point (keep thin)
├── pages/                 ← Multi-page Streamlit pages
│   ├── 01_pipeline_runner.py
│   └── 02_map_viewer.py
├── core/                  ← Business logic (no Streamlit imports here)
│   ├── fme_client.py
│   ├── claude_agent.py
│   └── geo_utils.py
├── data/                  ← Local data files (gitignored if large)
├── tests/                 ← pytest tests mirror core/ structure
└── .env                   ← Never committed
```

### Git Commit Convention
Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
```

---

### Step 5: Populate Zone 3 — Architecture Map (3-Layer Agent)

This is where your **3-layer agent architecture** gets documented. This zone is critical for AI agent work — Claude needs to understand which layer to generate code for.

```markdown
## ZONE 3: ARCHITECTURE MAP

### The 3-Layer Agent Architecture

This project uses a Directive → Orchestration → Execution agent pattern.
When generating code for agent functionality, always respect layer boundaries.

```
┌─────────────────────────────────────────────┐
│           LAYER 1: DIRECTIVE                │
│  (claude_agent.py → DirectiveAgent class)   │
│                                             │
│  • Receives natural language from user      │
│  • Interprets intent using Claude API       │
│  • Produces structured TaskSpec objects     │
│  • Does NOT execute tasks directly          │
└─────────────────┬───────────────────────────┘
                  │ TaskSpec (dataclass)
                  ▼
┌─────────────────────────────────────────────┐
│         LAYER 2: ORCHESTRATION              │
│  (orchestrator.py → PipelineOrchestrator)   │
│                                             │
│  • Receives TaskSpec from Directive layer   │
│  • Decides WHICH tools/pipelines to call   │
│  • Manages sequencing and dependencies     │
│  • Handles retries and error routing       │
│  • Returns ExecutionResult objects         │
└─────────────────┬───────────────────────────┘
                  │ ExecutionResult
                  ▼
┌─────────────────────────────────────────────┐
│           LAYER 3: EXECUTION                │
│  (fme_client.py, geo_utils.py, db.py)       │
│                                             │
│  • Direct API calls to FME Server          │
│  • PostGIS queries via psycopg2            │
│  • File I/O, coordinate transforms         │
│  • Returns raw results (no AI here)        │
└─────────────────────────────────────────────┘
```

### Key Data Structures

```python
# TaskSpec — output of Directive layer, input to Orchestration
@dataclass
class TaskSpec:
    intent: str              # e.g., "run_pipeline", "query_features"
    parameters: dict         # e.g., {"workspace": "ETL_Roads.fmw", "env": "prod"}
    priority: int            # 1=high, 3=low
    requires_confirmation: bool

# ExecutionResult — output of Execution layer
@dataclass
class ExecutionResult:
    success: bool
    data: Any                # GeoDataFrame, dict, string — depends on task
    error_message: str | None
    execution_time_seconds: float
    fme_job_id: str | None   # populated for FME tasks only
```

### Component Dependency Rules
- `core/` modules MUST NOT import from `pages/` or `app.py`
- `pages/` CAN import from `core/`
- Directive layer CAN import from Orchestration (to submit tasks)
- Orchestration CAN import from Execution
- Execution MUST NOT import from Directive or Orchestration
- **No circular imports. Ever.**

### External API Endpoints
- FME Server: `https://fmeserver.internal:8080/fmerest/v3/`
- PostGIS: `postgresql://user:***@db.internal:5432/gis_db`
  (credentials always from environment, never hardcoded)
```

---

### Step 6: Populate Zone 4 — Active State & Decision Log

This zone changes most frequently. Keep it honest — it's a living document.

```markdown
## ZONE 4: ACTIVE STATE

### Current Sprint Goal
> Implement the Directive layer's intent classification using Claude API
> so analysts can type natural language to trigger FME pipelines.

### Work In Progress
- [ ] `DirectiveAgent.parse_intent()` — 60% complete, test cases pending
- [ ] FME job polling with exponential backoff — not started
- [ ] Map layer toggle UI — complete, needs code review

### Known Issues & Workarounds
| Issue | Workaround | Fix Priority |
|-------|-----------|--------------|
| FME Server returns 202 but job silently fails | Poll `/jobs/{id}/status` 3x before marking done | High |
| GeoPandas CRS warning on EPSG:2193 → 4326 | Suppress with `warnings.filterwarnings` in geo_utils.py | Low |
| Streamlit rerenders full map on any state change | Use `st.cache_data` on GeoDataFrame fetch | Medium |

### Recent Decisions (Architectural)
| Date | Decision | Rationale |
|------|---------|-----------|
| 2024-01 | Use Folium over PyDeck | Better FME output format support |
| 2024-01 | TaskSpec as dataclass not Pydantic | Avoid dependency weight for internal objects |
| 2024-02 | Claude model pinned to sonnet | Haiku too weak for intent parsing edge cases |

### Next 3 TODOs (in order)
1. Write `test_directive_agent.py` with 10 intent classification test cases
2. Implement `PipelineOrchestrator.route_task()` method
3. Add run history table to PostGIS schema (migration file needed)

### Questions / Unresolved
- Should the Directive layer handle ambiguous intents by asking the user, or
  default to safest interpretation? (leaning toward: ask user)
```

---

### Step 7: Add GIS/FME-Specific Context Blocks

This is what makes your template domain-specific and genuinely valuable. Generic CLAUDE.md templates don't include this.

```markdown
## ZONE 5: GIS/FME CONTEXT

### Coordinate Reference Systems (CRS) Used in This Project
| CRS | EPSG | When Used |
|-----|------|-----------|
| NZTM2000 | 2193 | All source data from LINZ |
| WGS84 Geographic | 4326 | Map display (Folium default) |
| Web Mercator | 3857 | Tile layer backgrounds only |

**Rule:** All PostGIS storage is in EPSG:2193. All map display converts to
EPSG:4326. Conversions happen in `geo_utils.py::reproject_to_display()`.
Never convert CRS in a Streamlit page directly.

### FME Workspace Inventory
| Workspace File | Purpose | Typical Runtime | Params |
|---------------|---------|----------------|--------|
| `ETL_Roads.fmw` | LINZ roads → PostGIS | ~4 min | `env`, `update_mode` |
| `ETL_Parcels.fmw` | LINZ parcels → PostGIS | ~12 min | `env`, `region` |
| `Export_Shapefile.fmw` | PostGIS → Shapefile bundle | ~1 min | `layer`, `bbox` |

### FME Transformer Preferences
**Preferred transformers for common tasks:**
- Spatial filtering: `SpatialFilter` (not `AreaOnAreaOverlapper` — too slow)
- Attribute mapping: `AttributeRenamer` + `AttributeKeeper` (explicit is better)
- Reprojection: `Reprojector` with `EPSG:2193` as canonical source
- Geometry cleaning: `GeometryValidator` before any write operation

**Never suggest these without asking:**
- `FeatureReader` inside a workspace (performance trap — use separate workspace)
- `PythonCaller` for anything achievable with standard transformers
- `DatabaseJoiner` on large tables (use `FeatureMerger` with pre-filtered data)

### FME Server REST API Patterns
```python
# Approved FME Server call pattern
import requests
from dataclasses import dataclass

FME_BASE_URL = "https://fmeserver.internal:8080/fmerest/v3"

def submit_fme_job(workspace: str, parameters: dict) -> str:
    """Submit FME workspace job. Returns job_id."""
    response = requests.post(
        f"{FME_BASE_URL}/transformations/submit/{workspace}",
        json={"publishedParameters": parameters},
        headers={"Authorization": f"fmetoken token={FME_TOKEN}"},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["id"]

def poll_fme_job(job_id: str) -> str:
    """Poll job status. Returns: 'SUCCESS', 'FAILURE', 'RUNNING'"""
    response = requests.get(
        f"{FME_BASE_URL}/transformations/jobs/id/{job_id}",
        headers={"Authorization": f"fmetoken token={FME_TOKEN}"},
        timeout=10
    )
    return response.json()["status"]
```

### Spatial Data Quality Rules
- All inputs validated with `GeometryValidator` before PostGIS write
- Null geometries are logged and rejected (not silently dropped)
- Duplicate features checked by `source_id` + geometry hash
- Minimum polygon area: 1 square metre (smaller = topology error, reject)

### PostGIS Schema Conventions
```sql
-- All spatial tables follow this structure
CREATE TABLE gis.[layer_name] (
    id          SERIAL PRIMARY KEY,
    source_id   VARCHAR(50) NOT NULL,      -- original source identifier
    layer_name  VARCHAR(100) NOT NULL,
    geom        GEOMETRY(GEOMETRY, 2193),  -- always NZTM2000
    attributes  JSONB,                     -- flexible attribute storage
    loaded_at   TIMESTAMPTZ DEFAULT NOW(),
    fme_job_id  VARCHAR(50),               -- traceability to FME run
    is_current  BOOLEAN DEFAULT TRUE
);

CREATE INDEX ON gis.[layer_name] USING GIST (geom);
```
```

---

### Step 8: Test Your CLAUDE.md with Claude Code

Now validate that your CLAUDE.md actually works. This is the most satisfying step.

#### Test 1: Session Initialization Test

```bash
# Navigate to your project root (where CLAUDE.md lives)
cd ~/projects/your-gis-project

# Start a Claude Code session
claude

# In the Claude Code prompt, type:
> What coordinate system do we use for storing data in PostGIS, and why?
```

**Expected:** Claude should answer with EPSG:2193 / NZTM2000 and the rationale from your CLAUDE.md — without you explaining anything.

**If it fails:** Check that you're running `claude` from the directory containing `CLAUDE.md`. Claude Code automatically reads this file from the working directory.

#### Test 2: Architecture Boundary Test

```bash
# In Claude Code session:
> Write a function that calls the FME Server API and displays results
  directly in a Streamlit page.
```

**Expected:** Claude should push back or structure the response to respect your layer boundaries — FME calls go in `core/fme_client.py` (Execution layer), display logic goes in `pages/`. If Claude generates a monolithic function, your Zone 3 architecture map needs more explicit rules.

#### Test 3: Convention Enforcement Test

```bash
# In Claude Code session:
> Write a utility function to load a shapefile
```

**Expected output should:**
- Use type hints
- Use `pathlib.Path`
- Include `engine="pyogrio"` in the `read_file()` call
- Use `logging` not `print`
- Handle exceptions specifically

**Sample good output Claude should produce:**
```python
import logging
from pathlib import Path
import geopandas as gpd

logger = logging.getLogger(__name__)

def load_shapefile(file_path: Path, target_crs: int = 2193) -> gpd.GeoDataFrame:
    """
    Load a shapefile and reproject to target CRS.

    Args:
        file_path: Path to .shp file
        target_crs: EPSG code for output CRS (default: NZTM2000)

    Returns:
        GeoDataFrame in target CRS

    Raises:
        FileNotFoundError: If shapefile does not exist
        ValueError: If file cannot be read as valid spatial data
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Shapefile not found: {file_path}")

    try:
        gdf = gpd.read_file(file_path, engine="pyogrio")
        logger.info(f"Loaded {len(gdf)} features from {file_path.name}")
    except Exception as e:
        raise ValueError(f"Cannot read {file_path.name} as spatial data: {e}") from e

    if gdf.crs is None:
        raise ValueError(f"Shapefile {file_path.name} has no CRS defined")

    if gdf.crs.to_epsg() != target_crs:
        logger.info(f"Reprojecting from {gdf.crs.to_epsg()} to {target_crs}")
        gdf = gdf.to_crs(epsg=target_crs)

    return gdf
```

#### Test 4: Active State Awareness Test

```bash
# In Claude Code session:
> What should I work on next?
```

**Expected:** Claude should reference your Zone 4 "Next 3 TODOs" and suggest starting with the directive agent test cases.

#### Troubleshooting Common Issues

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Claude ignores CLAUDE.md | Not in project root | Run `claude` from the directory containing CLAUDE.md |
| Claude uses wrong model | Zone 2 not specific enough | Add explicit "DO NOT change this" warning |
| Claude violates layer boundaries | Zone 3 rules too vague | Add specific import restriction examples |
| Claude uses deprecated APIs | Missing in conventions | Add explicit "NEVER use X" list |

---

### Step 9: Templatize It for Reuse

Now extract a reusable template that works for *any* GIS/FME project — not just your specific one. This is what you'll publish.

Create a new file:

```bash
touch CLAUDE_TEMPLATE_GIS_FME.md
```

The key is replacing all project-specific values with clearly marked placeholders:

````markdown
# CLAUDE.md — GIS/FME Project Template

> **TEMPLATE INSTRUCTIONS (delete before using):**
> Replace all `[PLACEHOLDER]` values with your project specifics.
> Delete any zones not relevant to your project.
> This template follows the Ryan Wiggins Second Brain pattern.

---

> **For Claude:** Read this entire file before responding to any request.
> This is persistent context. Treat it as ground truth.

---

## ZONE 1: PROJECT IDENTITY

### Project Name
[YOUR PROJECT NAME]

### One-Line Purpose
[ONE SENTENCE: what it does, for whom, solving what problem]

### Primary Users
- [USER TYPE 1]
- [USER TYPE 2]
- [Developer/maintainer name]

### What Success Looks Like
[Describe the happy path in 2-3 sentences]

### Out of Scope
- [What this project explicitly does NOT do]

---

## ZONE 2: TECHNICAL STACK & CONVENTIONS

### Core Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Streamlit | [VERSION] |
| AI/LLM | Anthropic Claude API | [MODEL] |
| GIS Display | [Folium / PyDeck / Kepler.gl] | [VERSION] |
| Data | GeoPandas, Shapely | [VERSION] |
| FME Interface | [FME Server REST / FME Flow / FMEObjects] | [VERSION] |
| Database | [PostGIS / SQLite / None] | [VERSION] |

### Python Conventions

**ALWAYS:**
- [CONVENTION 1]
- [CONVENTION 2]

**NEVER:**
- [ANTI-PATTERN 1]
- [ANTI-PATTERN 2]

### Claude API Pattern
```python
# [YOUR STANDARD CLAUDE API CALL PATTERN]
```

### Project Structure
```
project_root/
├── CLAUDE.md
├── [YOUR STRUCTURE HERE]
```

---

## ZONE 3: ARCHITECTURE MAP

### Agent Layer Diagram
```
[PASTE YOUR LAYER DIAGRAM HERE — ASCII art works well]
```

### Key Data Structures
```python
# [YOUR CORE DATACLASSES OR MODELS]
```

### Dependency Rules
- [IMPORT RULE 1]
- [IMPORT RULE 2]

---

## ZONE 4: ACTIVE STATE

### Current Goal
> [CURRENT SPRINT OR MILESTONE IN ONE SENTENCE]

### Work In Progress
- [ ] [TASK 1] — [STATUS]
- [ ] [TASK 2] — [STATUS]

### Known Issues
| Issue | Workaround | Priority |
|-------|-----------|----------|
| [ISSUE] | [WORKAROUND] | [High/Med/Low] |

### Recent Decisions
| Date | Decision | Rationale |
|------|---------|-----------|
| [DATE] | [DECISION] | [WHY] |

### Next 3 TODOs
1. [TODO 1]
2. [TODO 2]
3. [TODO 3]

---

## ZONE 5: GIS/FME CONTEXT

### Coordinate Reference Systems
| CRS | EPSG | When Used |
|-----|------|-----------|
| [CRS NAME] | [EPSG] | [USE CASE] |

**Rule:** [YOUR CRS HANDLING RULE]

### FME Workspace Inventory
| Workspace | Purpose | Runtime | Parameters |
|-----------|---------|---------|-----------|
| `[workspace.fmw]` | [PURPOSE] | [TIME] | [PARAMS] |

### FME Transformer Preferences
**Preferred:**
- [TASK]: Use `[TransformerName]`

**Avoid:**
- `[TransformerName]` — [REASON]

### Spatial Data Rules
- [DATA QUALITY RULE 1]
- [DATA QUALITY RULE 2]

---

## MAINTENANCE

| Field | Value |
|-------|-------|
| Last updated | [DATE] |
| Owner | [NAME] |
| Update when | Any architectural decision, new convention, or sprint change |

---

## QUICK REFERENCE: WHAT TO ALWAYS CHECK BEFORE CODING

1. Which architecture layer does this code belong in?
2. Does this follow the CRS handling rules?
3. Which FME pattern applies?
4. Does this violate any NEVER convention?
````

---

### Step 10: Publish as a Build Post on Globe & Atlas

Structure your Build post to be genuinely useful to the GIS/AI community — not just a "here's what I did" summary.

**Recommended Post Structure:**

```markdown
# Build: Claude Code Second Brain Template for GIS/FME Projects

## What I Built
A CLAUDE.md template that gives Claude persistent context for GIS and FME
projects — based on Ryan Wiggins' second brain framework from the Peter Yang
YouTube series.

## The Problem It Solves
[2-3 sentences on the context problem]

## The Framework (5 Zones Explained)
[Brief explanation of each zone with GIS-specific examples]

## Download the Template
[Link to GitHub Gist or repo]

## How to Use It
1. Copy CLAUDE.md to your project root
2. Fill in the [PLACEHOLDER] values
3. Run `claude` from that directory
4. Test with these 4 validation prompts: [...]

## What I Learned
[2-3 genuine insights from building this]

## Next Version Ideas
- Auto-updating Active State from git log
- Multiple CLAUDE.md files per subdirectory
- CI check that CLAUDE.md stays up to date
```

**Publishing checklist:**

- [ ] Template is on GitHub (Gist or repo) with a public URL
- [ ] Post includes at least one concrete before/after Claude response example
- [ ] Post is tagged: `claude`, `gis`, `fme`, `streamlit`, `ai-tools`
- [ ] Post mentions the Peter Yang / Ryan Wiggins source video
- [ ] Post invites others to share their own CLAUDE.md patterns in comments

---

## 4. Validation

### How to Know You've Completed This Successfully

Run through this checklist. Every item should be a confident ✅.

#### File Completeness
- [ ] `CLAUDE.md` exists in your project root with all 5 zones populated
- [ ] All `[PLACEHOLDER]` text has been replaced with real content
- [ ] File is committed to git with a meaningful commit message
- [ ] `CLAUDE_TEMPLATE_GIS_FME.md` exists as a clean, reusable template

#### Content Quality
- [ ] Zone 1 describes your project specifically enough that a new developer could understand it without asking questions
- [ ] Zone 2 has at least 3 ALWAYS and 3 NEVER conventions, all GIS/FME-relevant
- [ ] Zone 3 has an ASCII diagram of your 3-layer architecture
- [ ] Zone 4 has at least 3 current TODOs and 2 recent decisions
- [ ] Zone 5 has your actual CRS rules and at least 2 FME workspace entries

#### Functional Tests Passed
- [ ] **Test 