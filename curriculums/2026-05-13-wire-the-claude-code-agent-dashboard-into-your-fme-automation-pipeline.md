# Wire the Claude Code Agent Dashboard into Your FME Automation Pipeline

## A Hands-On Tutorial for GIS Practitioners

---

## 1. Introduction & Context

### What Is This?

Claude Code recently shipped an **agent dashboard** — a visual supervisory layer on top of the CLI tool that lets you watch, pause, and interrogate multi-step AI agent runs in real time. Instead of staring at a scrolling terminal hoping your automation doesn't go sideways, you now have a structured view of every agent step, its status, and where it failed or stalled.

For GIS practitioners using **FME (Feature Manipulation Engine)** to build ETL pipelines, this matters a great deal. FME workspace authoring is inherently multi-step: reading spatial data, applying transformers, writing outputs, handling coordinate systems, validating geometries. When you hand off authoring tasks to a Claude Code agent, errors are inevitable — and until now, diagnosing *which step* caused them required painful terminal archaeology.

### Why It's Worth Learning

| Before Agent Dashboard | After Agent Dashboard |
|---|---|
| Errors buried in terminal scroll | Errors surfaced per-step, with context |
| Guessing which directive caused a halt | Pinpoint the failing agent action |
| Reactive CLAUDE.md tuning | Evidence-based directive refinement |
| Hard to explain AI-assisted ETL to stakeholders | Shareable, structured session documentation |

This tutorial teaches you to:
1. Set up Claude Code with the agent dashboard for an FME session
2. Instrument your CLAUDE.md directives for FME-specific workflows
3. Capture and categorize agent errors
4. Refine your directives using real evidence
5. Write a "Build post" documenting your before/after for the GIS community

---

## 2. Prerequisites

### Software & Accounts

- [ ] **Claude Code CLI** installed and authenticated (`claude --version` returns a result)
- [ ] **FME Desktop** (2023.x or later) installed and licensed
- [ ] **FME Flow** (optional, but recommended for automation scheduling)
- [ ] A code editor — VS Code recommended
- [ ] **Git** installed (for versioning your CLAUDE.md changes)
- [ ] A Markdown editor or **Notion/Hashnode/Dev.to** account for the Build post

### Knowledge Assumptions

- You have run at least one Claude Code session from the CLI before
- You understand basic FME concepts: workspaces, readers, writers, transformers
- You are comfortable editing plain-text configuration files
- You have a working FME workspace (`.fmw` file) you want to automate or improve — if not, we provide a sample below

### Verify Your Claude Code Installation

```bash
# Check Claude Code version — should be recent enough to include agent dashboard
claude --version

# Check you can authenticate
claude auth status

# Launch a quick sanity-check session
claude "say hello" --no-stream
```

If the agent dashboard is available, you should see dashboard-related flags when you run:

```bash
claude --help | grep -i dashboard
# or
claude --help | grep -i agent
```

---

## 3. Step-by-Step Guide

---

### Phase 1: Prepare Your FME Workspace & Project Structure

#### Step 1.1 — Organize Your Project Directory

Create a clean working directory that Claude Code will use as its context root.

```bash
mkdir fme-claude-pipeline
cd fme-claude-pipeline

# Create the expected folder structure
mkdir -p workspaces
mkdir -p logs/agent-sessions
mkdir -p directives
mkdir -p exports

# Initialize git for tracking CLAUDE.md changes over time
git init
```

Your directory should look like this:

```
fme-claude-pipeline/
├── CLAUDE.md                    ← Agent directives (we'll build this)
├── workspaces/
│   └── my_etl_workspace.fmw    ← Your FME workspace file
├── logs/
│   └── agent-sessions/          ← Agent run logs go here
├── directives/
│   └── CLAUDE.md.v1.backup      ← Versioned backups of directives
└── exports/                     ← FME output data lands here
```

#### Step 1.2 — Place Your FME Workspace

Copy your existing `.fmw` file into `workspaces/`. If you don't have one, create a minimal test workspace using the FME Workbench GUI:

**Sample minimal workspace tasks for testing:**
- Reader: CSV with latitude/longitude columns
- Transformer: `Reprojector` (WGS84 → Web Mercator)
- Transformer: `GeometryFilter` (filter out null geometries)
- Writer: GeoJSON output

Save it as `workspaces/test_etl.fmw`.

#### Step 1.3 — Create Your Baseline CLAUDE.md

This is your agent instruction file. Start with a **v1 baseline** — deliberately incomplete — so you can measure improvement later.

```bash
touch CLAUDE.md
```

Paste the following into `CLAUDE.md`:

```markdown
# CLAUDE.md — FME ETL Automation Directives

## Project Context
This project uses FME Desktop to build and modify spatial ETL workspaces.
Your job is to help author, debug, and optimize FME workspaces (.fmw files).

## FME Environment
- FME version: 2023.2 (update to match yours)
- FME CLI path: /Applications/FME/fme   # macOS example
  # Windows: C:\Program Files\FME\fme.exe
  # Linux: /opt/fme/fme
- Workspace directory: ./workspaces/
- Output directory: ./exports/

## Allowed Actions
- Read and analyze .fmw workspace XML
- Run FME workspaces via CLI: `fme <workspace.fmw> --log-file <path>`
- Suggest transformer additions or modifications
- Parse FME log files for errors

## Current Task
Analyze the workspace in ./workspaces/ and report:
1. What transformers are present
2. Whether the workspace runs successfully
3. Any warnings in the log output
```

> **Note:** This v1 is intentionally sparse. We will observe what breaks and improve it in Phase 3.

---

### Phase 2: Launch Claude Code with the Agent Dashboard

#### Step 2.1 — Start a Claude Code Agent Session

Navigate to your project root and launch Claude Code in agent mode with the dashboard enabled:

```bash
cd fme-claude-pipeline

# Launch Claude Code — the agent dashboard should open automatically
# in a browser tab or separate terminal pane depending on your version
claude

# If your version requires an explicit flag:
claude --agent-dashboard
# or
claude --dashboard
```

> **Tip:** Check the [Claude Code changelog](https://docs.anthropic.com/claude-code) for the exact flag name in your installed version, as the dashboard feature may use slightly different syntax across releases.

#### Step 2.2 — Understand the Dashboard Layout

Once the dashboard opens, familiarize yourself with these sections:

```
┌─────────────────────────────────────────────────────────┐
│  CLAUDE CODE AGENT DASHBOARD                            │
├──────────────────┬──────────────────────────────────────┤
│  AGENT STEPS     │  STEP DETAIL                         │
│  ─────────────── │  ───────────────────────────────────  │
│  ✅ Step 1        │  Tool: bash                          │
│  ✅ Step 2        │  Command: fme test_etl.fmw           │
│  ❌ Step 3        │  Status: FAILED                      │
│  ⏳ Step 4        │  Error: Coordinate system not found  │
│                  │                                       │
├──────────────────┴──────────────────────────────────────┤
│  TOOL CALLS  │  MEMORY  │  PERMISSIONS  │  LOGS          │
└─────────────────────────────────────────────────────────┘
```

**Key panels to watch:**
- **Agent Steps** — the sequential list of actions the agent is taking
- **Step Detail** — inputs, outputs, and errors for the selected step
- **Tool Calls** — which tools (bash, file read/write, etc.) were invoked
- **Permissions** — any actions the agent wants to take that need your approval

#### Step 2.3 — Give Claude Code Your First FME Task

In the Claude Code chat input, type:

```
Analyze the FME workspace at ./workspaces/test_etl.fmw. 
Run it using the FME CLI and capture the log output. 
Report what transformers are present, whether it ran successfully, 
and list any errors or warnings from the log.
Save the log to ./logs/agent-sessions/session-001.log
```

**Watch the dashboard as Claude Code works.** You should see it:
1. Read the `.fmw` file (XML parsing step)
2. Construct an `fme` CLI command
3. Execute the workspace
4. Read the output log
5. Summarize findings

#### Step 2.4 — Log Your Observations in a Session Notes File

While the agent runs, open a second terminal and create a live observation log:

```bash
touch logs/agent-sessions/session-001-observations.md
```

Use this template to record what you see:

```markdown
# Agent Session 001 — Observations
Date: YYYY-MM-DD
Task: Initial FME workspace analysis

## Step-by-Step Notes

| Step # | Dashboard Status | Tool Used | What Happened | Error? |
|--------|-----------------|-----------|---------------|--------|
| 1      | ✅              | file_read  | Read .fmw XML |  No    |
| 2      | ❌              | bash       | fme CLI run   | Yes — path not found |
| 3      | ✅              | file_read  | Read log file | No    |

## Errors Encountered
- [ ] List each unique error type here

## Unexpected Halts
- [ ] Document any steps where the agent paused waiting for input

## Directive Gaps Identified
- [ ] List CLAUDE.md omissions that caused confusion
```

---

### Phase 3: Capture Errors and Identify Directive Gaps

#### Step 3.1 — Run Three Different FME Task Types

To get meaningful error data, run the agent on **three different task categories**. After each run, update your observations log.

**Task A — Workspace Execution:**
```
Run the workspace ./workspaces/test_etl.fmw with FME CLI. 
If it fails, diagnose the error from the log and suggest a fix.
```

**Task B — Workspace Modification:**
```
Open ./workspaces/test_etl.fmw and add a StatisticsCalculator 
transformer after the GeometryFilter. Save the modified workspace.
```

**Task C — Log Analysis:**
```
Parse ./logs/agent-sessions/session-001.log and produce a 
structured summary of: total features processed, any FATAL errors, 
any coordinate system warnings, and elapsed time.
```

#### Step 3.2 — Categorize Your Errors

After running all three tasks, tally your observations. Common error categories you'll encounter with FME + Claude Code:

```markdown
## Error Category Tally

### Category 1: Path/Environment Errors
- FME CLI not found at expected path
- Workspace file path incorrect
- Output directory doesn't exist
Occurrences: ___

### Category 2: FME Domain Knowledge Gaps
- Agent suggested non-existent transformer names
- Incorrect XML schema for .fmw modifications
- Wrong FME CLI flag syntax
Occurrences: ___

### Category 3: Permission/Safety Halts
- Agent paused before writing to filesystem
- Agent asked for confirmation before running CLI command
Occurrences: ___

### Category 4: Context Loss
- Agent forgot earlier task context mid-session
- Agent repeated work already completed
Occurrences: ___
```

#### Step 3.3 — Map Errors Back to Missing Directives

For each error category, identify what CLAUDE.md instruction would have prevented it:

| Error Observed | Root Cause | Directive to Add |
|---|---|---|
| FME CLI path wrong | Path not specified in CLAUDE.md | Add exact CLI path |
| Agent invented transformer name | No FME transformer reference | Add known transformer list |
| Agent halted asking permission | No pre-authorization for CLI runs | Add explicit permission grant |
| Agent re-read workspace twice | No instruction to cache XML parse | Add "parse workspace once" directive |

---

### Phase 4: Refine Your CLAUDE.md (v2)

#### Step 4.1 — Back Up v1

```bash
cp CLAUDE.md directives/CLAUDE.md.v1.backup
git add .
git commit -m "v1 baseline CLAUDE.md before error analysis"
```

#### Step 4.2 — Write Your Improved CLAUDE.md v2

Replace the contents of `CLAUDE.md` with a hardened version. Here is a **comprehensive template** — customize based on *your actual observed errors*:

```markdown
# CLAUDE.md — FME ETL Automation Directives (v2)
# Last updated: YYYY-MM-DD
# Changes from v1: Added FME paths, transformer catalog, 
#                  permissions, error handling protocols

---

## 1. Project Context

This project automates the authoring and execution of FME (Feature 
Manipulation Engine) workspaces for spatial ETL.

**Your role:** FME workspace analyst, debugger, and modifier.
**You are NOT:** a general coding assistant in this context. 
All tasks relate to FME workspace files and FME CLI operations.

---

## 2. Environment Configuration

### FME CLI Paths (use EXACTLY these paths — do not guess)
```
# macOS
FME_CLI=/Applications/FME/fme

# Windows (use this format in bash commands)
FME_CLI="C:/Program Files/FME/fme.exe"

# Linux
FME_CLI=/opt/fme/fme
```

### Directory Structure
```
PROJECT_ROOT=./                         # You are always run from here
WORKSPACE_DIR=./workspaces/             # All .fmw files live here
LOG_DIR=./logs/agent-sessions/          # Write all logs here
EXPORT_DIR=./exports/                   # FME output data goes here
```

---

## 3. Pre-Authorized Actions

You MAY perform the following without asking for confirmation:
- Read any file in this project directory
- Write to ./logs/ and ./exports/ directories
- Run FME CLI commands in read-only mode (--no-output flag)
- Modify files in ./workspaces/ ONLY IF the user has said "proceed"

You MUST ask for confirmation before:
- Deleting any file
- Running FME with write operations on non-test data
- Making changes to files outside this project directory

---

## 4. FME Workspace Format Reference

FME workspaces are XML files. Key XML elements:
```xml
<WORKSPACE>
  <READER TYPE="...">         <!-- Data source definition -->
  <WRITER TYPE="...">         <!-- Output definition -->
  <TRANSFORMER ...>           <!-- Processing step -->
  <PARAMETER ...>             <!-- Configuration -->
</WORKSPACE>
```

### Verified FME Transformer Names (use ONLY these spellings)
- Reprojector
- GeometryFilter  
- StatisticsCalculator
- AttributeRenamer
- AttributeKeeper
- Clipper
- Dissolver
- FeatureMerger
- GeometryValidator
- NullAttributeMapper

**IMPORTANT:** Do not invent transformer names. If unsure, 
say "I don't know this transformer" rather than guessing.

---

## 5. FME CLI Usage

### Run a workspace:
```bash
$FME_CLI <workspace.fmw> \
  --log-file ./logs/agent-sessions/<session-id>.log \
  --log-level 5
```

### Run in test mode (no data written):
```bash
$FME_CLI <workspace.fmw> \
  --test-mode yes \
  --log-file ./logs/agent-sessions/<session-id>.log
```

### Parse log for errors only:
```bash
grep -E "ERROR|FATAL|WARNING" ./logs/agent-sessions/<session-id>.log
```

---

## 6. Error Handling Protocol

When an FME CLI run fails:
1. Read the full log file immediately
2. Search for lines containing "ERROR" or "FATAL"  
3. Report the error message verbatim — do not paraphrase
4. Check if error is in this known-error table:

| Error Pattern | Likely Cause | Suggested Fix |
|---|---|---|
| "Coordinate system not found" | Missing EPSG code | Check Reprojector parameters |
| "Unable to open dataset" | Wrong file path in Reader | Verify SOURCE_DATASET parameter |
| "Feature class does not exist" | Layer name mismatch | Check FEATURE_TYPES in Reader |
| "License not available" | FME license expired | Check with system admin |

---

## 7. Session Discipline

- Parse the workspace XML **once** per session and reference 
  your parsed result — do not re-read the file on each step
- After completing a task, summarize what you did in 3 bullet points
- If you are uncertain about an FME-specific behavior, 
  say so explicitly rather than proceeding with a guess
- Log every CLI command you run to the session log

---

## 8. Output Format

Always structure your final response as:

```
## Task Summary
[What was asked]

## Actions Taken
1. [Step 1]
2. [Step 2]

## Result
[Success/Failure + details]

## Errors Found
[List or "None"]

## Recommended Next Steps
[Your suggestions]
```
```

#### Step 4.3 — Commit v2

```bash
git add CLAUDE.md
git commit -m "v2 CLAUDE.md: hardened based on session-001 error analysis

Changes:
- Added explicit FME CLI paths
- Added pre-authorization for safe actions
- Added transformer name allowlist
- Added error handling protocol
- Added FME XML schema reference
- Added session discipline rules"
```

---

### Phase 5: Run a Validation Session

#### Step 5.1 — Repeat Your Three Tasks with v2

Rerun Tasks A, B, and C from Phase 3 using the same inputs. Create a new observation log:

```bash
touch logs/agent-sessions/session-002-observations.md
```

Use the same template as session-001 so you have a direct comparison.

#### Step 5.2 — Compare Error Rates

```bash
# Count error steps in session 001
grep -c "❌" logs/agent-sessions/session-001-observations.md

# Count error steps in session 002  
grep -c "❌" logs/agent-sessions/session-002-observations.md
```

Build a comparison table:

```markdown
## Before/After Comparison

| Metric | v1 (Session 001) | v2 (Session 002) | Improvement |
|--------|-----------------|-----------------|-------------|
| Total agent steps | ___ | ___ | — |
| Steps with errors | ___ | ___ | ___% reduction |
| Unexpected halts | ___ | ___ | ___% reduction |
| Tasks completed successfully | ___/3 | ___/3 | — |
| Avg steps to task completion | ___ | ___ | — |
```

---

### Phase 6: Write Your Build Post

#### Step 6.1 — Build Post Structure

Create the post draft:

```bash
touch build-post-draft.md
```

Use this proven structure for a GIS practitioner audience:

```markdown
# How I Used the Claude Code Agent Dashboard to 
# Supervise AI-Assisted FME ETL Authoring

## The Problem I Was Solving
[1-2 paragraphs: what you were trying to automate in FME 
and why you wanted AI assistance]

## What the Claude Code Agent Dashboard Is
[Brief explanation for readers who haven't seen it — 
include a screenshot of the dashboard with labels]

## My Setup
[Directory structure, CLAUDE.md v1, the three test tasks]

## What I Observed: The Errors That Surfaced
[Your categorized error table from Phase 3]

## Screenshots / Dashboard Evidence
[Insert screenshots of failing steps in the dashboard — 
this is the key visual that makes the post credible]

## What I Changed: CLAUDE.md v1 → v2
[Show a diff or before/after of key directive changes]

## The Results
[Your before/after comparison table from Phase 5]

## Key Lessons for GIS Practitioners Using AI for ETL

1. **Name your tools explicitly** — AI agents don't know 
   FME's transformer vocabulary by default. An allowlist 
   prevents hallucinated transformer names.

2. **Pre-authorize safe operations** — Claude Code's 
   cautious permission model is great for safety but 
   interrupts flow. Tell it explicitly what it can do 
   without asking.

3. **The dashboard is a directive feedback loop** — 
   Every error you see is a missing or ambiguous instruction.

4. **Log everything from day one** — The agent dashboard 
   gives you the structure; you need the discipline to 
   capture observations while the session runs.

## My v2 CLAUDE.md Template (Gist / GitHub Link)
[Share your hardened template for other FME users]

## What I'm Doing Next
[Your next iteration — e.g., adding FME Flow API calls, 
integrating with a spatial database, etc.]
```

#### Step 6.2 — Add Screenshots

Capture and annotate these screenshots for maximum reader value:

1. **Dashboard overview** — full panel layout labeled
2. **A failing step** — showing error message in Step Detail
3. **A permission halt** — showing the agent waiting for confirmation
4. **The diff** — CLAUDE.md v1 vs v2 key changes
5. **Before/after error table** — your comparison metrics

#### Step 6.3 — Publish

Recommended platforms for GIS/data engineering audiences:
- **Esri Community** (if you also use ArcGIS stack)
- **Safe Software Community** (FME-specific audience — ideal)
- **Dev.to** or **Hashnode** (developer-general)
- **LinkedIn Article** (practitioner reach)

---

## 4. Validation

Use this checklist to confirm you have successfully completed the exercise:

### Setup Validation
- [ ] `fme-claude-pipeline/` directory exists with correct structure
- [ ] CLAUDE.md v1 committed to git
- [ ] Claude Code agent dashboard launched and accessible
- [ ] FME workspace runs successfully via CLI (outside of agent)

### Session Validation
- [ ] At least 3 agent tasks completed (Tasks A, B, C)
- [ ] `session-001-observations.md` populated with step-by-step notes
- [ ] Error categories identified and tallied
- [ ] Directive gaps mapped to specific CLAUDE.md omissions

### CLAUDE.md Validation
- [ ] CLAUDE.md v2 includes explicit FME CLI paths
- [ ] CLAUDE.md v2 includes a transformer name allowlist
- [ ] CLAUDE.md v2 includes pre-authorized action list
- [ ] CLAUDE.md v2 includes an error handling protocol
- [ ] v1 backed up to `directives/CLAUDE.md.v1.backup`
- [ ] Git commit message explains what changed and why

### Comparison Validation
- [ ] `session-002-observations.md` completed with v2 CLAUDE.md active
- [ ] Before/after comparison table shows measurable improvement
- [ ] Error rate reduction is documented with actual numbers

### Build Post Validation
- [ ] Draft covers all six sections from the template
- [ ] At least 2 screenshots included
- [ ] CLAUDE.md template shared publicly (Gist or repo)
- [ ] Post published to at least one platform

**You've fully completed this exercise when** your published post includes a before/after comparison table with real session data and links to your v2 CLAUDE.md template.

---

## 5. Next Steps

### Immediate (Next Session)
- **Iterate CLAUDE.md to v3** — One session with v2 will surface new, more subtle issues. The directive file is a living document.
- **Add FME Flow API calls** — Extend the agent to schedule workspace runs via FME Flow REST API, not just local CLI execution
- **Create task-specific CLAUDE.md sections** — Add separate sections for "Workspace Authoring" vs "Log Analysis" vs "Data Validation" tasks

### Short-Term (Next 2 Weeks)
- **Build a CLAUDE.md library** — Create modular directive snippets for common FME operations (coordinate reprojection, format conversion, spatial joins) that you can compose per-project
- **Instrument FME log parsing** — Write a Python script that post-processes FME logs into a structured JSON format that Claude Code can analyze more reliably
- **Multi-workspace orchestration** — Use Claude Code to manage a pipeline of chained FME workspaces, with the agent dashboard giving you visibility across the entire chain

### Longer-Term (1+ Month)
- **Contribute to the community** — Share your CLAUDE.md templates in the Safe Software Community forum specifically as "AI Agent Directives for FME" — this is genuinely novel and useful
- **Evaluate competing approaches** — Compare Claude Code + FME against GitHub Copilot + FME Python API and document the tradeoffs
- **Build an error pattern library** — After 10+ sessions, you'll have enough error data to write a formal "Common Claude Code Failure Modes in FME Workflows" reference guide

### Related Learning
- [FME CLI Documentation](https://docs.safe.com/fme/html/FME_Desktop_Documentation/FME_ReadersWriters/aboutFME/FME_CLI.htm) — Master the CLI options Claude Code will invoke
- [Claude Code Documentation](https://docs.anthropic.com/claude-code) — Stay current on new dashboard features
- [FME Workspace XML Schema](https://docs.safe.com/fme/) — Understanding the XML helps you write better prompts and catch agent errors

---

## Quick Reference Card

```
DAILY WORKFLOW WITH AGENT DASHBOARD
─────────────────────────────────────
1. cd fme-claude-pipeline
2. claude (dashboard opens)
3. Paste task prompt
4. Watch dashboard — note any ❌ steps
5. After session: update observations.md
6. Weekly: review patterns → update CLAUDE.md
7. Monthly: publish improvements as Build post
─────────────────────────────────────
KEY FILES:
  CLAUDE.md              ← Edit this to fix recurring errors
  logs/agent-sessions/   ← Evidence for directive decisions
  directives/*.backup    ← Never delete old versions
─────────────────────────────────────
CLAUDE.md EDIT TRIGGERS:
  Path error           → Add explicit path
  Hallucinated tool    → Add to allowlist
  Repeated question    → Add pre-authorization
  Context loss         → Add "remember X" directive
  Wrong output format  → Add format template
```

---

*Tutorial version: 1.0 | Applies to: Claude Code with Agent Dashboard, FME 2023.x+*