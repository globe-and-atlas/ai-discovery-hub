# Wire the Claude Code Agent Dashboard into Your FME Automation Pipeline

> **Honest upfront note:** The source video (Nate Herk | AI Automation, YouTube) was inaccessible for content extraction — only metadata was returned. Rather than invent specific commands, flags, or UI steps I cannot verify, I'll clearly mark which sections are grounded in **established Claude Code CLI knowledge** versus what you should **confirm against the video** before running in production. Everything here is actionable, but treat the dashboard-specific steps as a starting framework to refine after you watch the video yourself.

---

## 1. Introduction & Context

You're already using Claude Code CLI to generate and refactor FME workspaces, write Python Caller scripts, and orchestrate multi-step ETL logic. That works — but until now, supervising a long multi-step agent run meant staring at terminal scrollback and hoping nothing quietly derailed three steps ago.

The **Claude Code Agent Dashboard** changes the supervision model. Instead of a linear log stream, you get a visual layer over the agent's step-by-step execution: which tools it called, which steps errored, where it halted waiting for clarification, and how long each step took. For FME automation specifically, this matters because:

- FME workspace authoring via AI produces **chains of decisions** (schema mapping → transformer selection → parameter tuning → output format). Any broken link in that chain silently propagates bad output.
- Your `CLAUDE.md` directives govern the agent's behavior, but without step visibility you're tuning blindly.
- A **before/after Build post** showing real error patterns is exactly the kind of practitioner-credible content that resonates with the GIS community on LinkedIn or Esri Community.

**What you'll build by the end of this tutorial:**

1. A running Claude Code session with the agent dashboard active, connected to an FME workspace automation task
2. A structured error log capturing which agent steps fail most often
3. Refined `CLAUDE.md` directives based on observed failure patterns
4. A draft Build post outline ready for publication

---

## 2. Prerequisites

### Tools & Accounts

| Requirement | Notes |
|---|---|
| **Claude Code CLI** | Installed and authenticated (`claude --version` returns without error) |
| **Anthropic account** | With Claude Code access enabled |
| **FME Form or FME Flow** | Version 2023.x or later recommended; 2024.x preferred |
| **An existing FME workspace** | Something with at least 3–5 transformers so there's real complexity for the agent to reason about |
| **Node.js ≥ 18** or **Python ≥ 3.10** | Depending on how you've scaffolded your Claude Code integration |
| **A text editor** | VS Code recommended; the dashboard may integrate here |

### Files You Should Have Ready

```
your-project/
├── CLAUDE.md                  # Your existing directives file (or create one)
├── workspace/
│   └── your_etl.fmw           # The FME workspace you'll use as the test target
├── scripts/
│   └── fme_runner.py          # Script that invokes FME Engine or FME Flow REST API
└── logs/
    └── .gitkeep               # Where you'll capture agent step logs
```

### Knowledge Baseline

- You know how to run `claude` from the terminal and have previously given it multi-step instructions
- You understand FME's basic transformer model (Readers → Transformers → Writers)
- You've read or written at least a minimal `CLAUDE.md` file before

> **If you don't have a `CLAUDE.md` yet**, create one now at the root of your project. It's just a Markdown file — Claude Code reads it automatically as persistent context. Start with this shell:

```markdown
# CLAUDE.md — FME Workspace Automation Agent

## Role
You are an FME workspace automation assistant. Your job is to generate,
modify, and validate FME workspaces and associated Python scripts.

## Constraints
- Never remove existing Readers or Writers without explicit confirmation
- Always preserve coordinate system definitions on all geometry features
- When uncertain about a transformer parameter, ask before assuming
- Output all workspace changes as FME Python API calls, not raw XML edits

## FME Environment
- FME Version: 2024.x
- Python Environment: fme_runner.py handles all subprocess calls
- Log output directory: ./logs/

## Known Problem Areas (update this section as you learn)
- [empty — you'll fill this in after the exercise]
```

---

## 3. Step-by-Step Guide

### Step 3.1 — Verify Your Claude Code CLI Version

Before enabling any dashboard features, confirm you're on a version that includes the agent dashboard. Open your terminal:

```bash
claude --version
```

> **⚠️ Source gap:** The video likely specifies the minimum version that ships with the agent dashboard. Watch the first two minutes of [the video](https://www.youtube.com/watch?v=ZAaxx3qyT8g) and note the version shown. If your version is older, run:

```bash
# Update via npm (if installed that way)
npm update -g @anthropic-ai/claude-code

# Or check Anthropic's official install docs for your method
```

---

### Step 3.2 — Launch Claude Code with Agent Dashboard Enabled

> **⚠️ Source gap:** The exact flag or command to activate the dashboard UI is in the video and I cannot confirm it from the metadata alone. The pattern is likely one of the following — **verify against the video before using**:

```bash
# Likely pattern A — dashboard flag
claude --dashboard

# Likely pattern B — UI mode
claude --ui

# Likely pattern C — it opens automatically in newer versions
claude
```

Once launched, you should see a panel (either in-terminal or in a browser tab) showing:
- A list of agent steps / tool calls
- Status indicators (running / complete / error)
- Token usage per step
- Tool call details (what the agent asked, what came back)

**Take a screenshot of this initial view.** You'll use it in your Build post as the "before" state.

---

### Step 3.3 — Set Up Your FME Automation Task

You need a realistic task that will produce enough agent steps to observe meaningful patterns. Here's a good starting prompt that will generate 8–12 distinct agent steps:

Create a file called `task_prompt.md` in your project root:

```markdown
# Task: Refactor ETL Workspace for New Source Schema

## Context
I have an FME workspace at `workspace/your_etl.fmw` that reads from a
PostgreSQL/PostGIS source. The source schema has changed:
- Table `parcels` now has column `land_use_code` (was `lu_code`)
- A new column `last_updated` (TIMESTAMP) has been added
- The geometry column is now `shape` (was `geom`)

## What I need you to do
1. Read the current workspace using the FME Python API
2. Identify all attribute references to the old column names
3. Update AttributeRenamer or AttributeManager transformers accordingly
4. Add a schema validation check against the new column list
5. Update the workspace description with today's date and change summary
6. Run the workspace against the sample data in `data/sample_parcels.gpkg`
7. Confirm output row count matches input row count
8. Write a summary of all changes made to `logs/refactor_log.md`

## Constraints
Follow all rules in CLAUDE.md.
```

Now start the agent session pointing at this task:

```bash
# From your project root
claude task_prompt.md
```

> If the dashboard is flag-activated, add the appropriate flag here.

---

### Step 3.4 — Observe and Log Agent Steps in Real Time

As the agent runs, your job is **not to intervene** on the first pass. Let it run to completion (or failure). While it runs:

**Open `logs/session_001.md`** in a split editor and manually note:

```markdown
# Session 001 — FME Schema Refactor
Date: YYYY-MM-DD
Task: Schema column rename refactor

## Step Log

| Step # | Tool Called | Status | Notes |
|--------|-------------|--------|-------|
| 1 | read_file (workspace/your_etl.fmw) | ✅ Complete | |
| 2 | bash (fme_python_api call) | ❌ Error | FME Python not in PATH |
| 3 | ... | | |

## Error Patterns Observed
- [ ] PATH/environment issues
- [ ] Incorrect FME transformer parameter names
- [ ] Hallucinated transformer names (transformers that don't exist)
- [ ] Coordinate system handling errors
- [ ] Wrong FME Python API method signatures
- [ ] File path assumptions (Windows vs. Unix separators)
- [ ] Premature "done" without validation step

## Unexpected Halts
- Step # ___: Reason: ___

## Successful Patterns Worth Keeping
- ___
```

> **Pro tip:** If the dashboard shows step durations, note which steps are slow. Slow steps often indicate the agent is making many tool calls trying to recover from an error it didn't surface clearly.

---

### Step 3.5 — Run a Second Session with Intentional Observation Points

After the first run, run it again — this time with a `--verbose` or equivalent flag to get maximum detail in the dashboard:

```bash
# Verbose mode (confirm exact flag from video)
claude --verbose task_prompt.md
```

This time, when you see the agent about to make a step you've already flagged as error-prone, use the dashboard's **interrupt/pause** capability (if available — confirm from video) to inspect the tool call before it executes.

The goal is to catch the moment the agent makes a wrong assumption about your FME environment.

---

### Step 3.6 — Extract the Error Pattern Taxonomy

After two sessions, consolidate your observations. Here's a taxonomy that commonly emerges from FME + AI agent combinations:

```markdown
## FME Agent Error Taxonomy (fill in your counts)

### Category 1: Environment Errors
- FME Python API not on PATH: [N occurrences]
- Wrong FME version assumed: [N occurrences]
- Wrong OS path separator: [N occurrences]

### Category 2: FME Domain Knowledge Errors  
- Hallucinated transformer name (e.g., "AttributeUpdater" instead of "AttributeManager"): [N]
- Wrong parameter name for known transformer: [N]
- Incorrect FME attribute syntax (missing @ prefix, etc.): [N]

### Category 3: Task Reasoning Errors
- Skipped validation step: [N]
- Declared success before checking output: [N]
- Overwrote file without backup: [N]

### Category 4: Coordination Errors (multi-step breakdown)
- Lost context from step 1 by step 6: [N]
- Re-read file already processed: [N]
```

---

### Step 3.7 — Refine Your `CLAUDE.md` Based on Evidence

Now translate your error taxonomy directly into `CLAUDE.md` improvements. Here's the before/after pattern:

**Before (generic):**
```markdown
## Constraints
- Never remove existing Readers or Writers without explicit confirmation
- Always preserve coordinate system definitions on all geometry features
```

**After (evidence-based):**
```markdown
## Constraints
- Never remove existing Readers or Writers without explicit confirmation
- Always preserve coordinate system definitions on all geometry features

## Environment — Read This First
- FME Python API location: `/path/to/fme/python/fmeobjects`
  Add this to sys.path before any import: `sys.path.insert(0, '/path/to/fme/python/fmeobjects')`
- FME executable: `/usr/local/fme/fme` (Linux) or `C:\FME\fme.exe` (Windows)
- All paths use forward slashes even on Windows (FME handles this)

## FME Transformer Reference — Verified Names Only
Use ONLY these transformer names (do not invent variations):
- AttributeManager (not AttributeUpdater, not AttributeEditor)
- AttributeRenamer
- Tester
- GeometryValidator
- StatisticsCalculator

## Validation Requirements — Non-Negotiable
After every workspace modification:
1. Read back the modified workspace and confirm the changed attribute names exist
2. Run the workspace with `--log-level 3` and check for WARN or ERROR lines
3. Compare input feature count to output feature count
4. Only then write the success summary

## Known Failure Modes (observed in sessions 001-002)
- The agent tends to skip step 7 (validation) when step 6 succeeds quickly — explicitly re-state validation in every task prompt
- FME transformer parameter names are inconsistently named in training data — always verify against the FME documentation API reference provided below
```

---

### Step 3.8 — Run a Third Session to Validate Improvements

With your refined `CLAUDE.md`, run the same task again:

```bash
claude task_prompt.md
```

This time, track the same metrics:
- Number of errors
- Number of unexpected halts
- Steps where agent asked for clarification vs. assumed

Fill in a comparison table:

```markdown
## Session Comparison

| Metric | Session 001 | Session 002 | Session 003 (after CLAUDE.md update) |
|--------|-------------|-------------|--------------------------------------|
| Total errors | | | |
| Unexpected halts | | | |
| Transformer hallucinations | | | |
| Validation steps completed | | | |
| Task completed successfully | | | |
| Wall-clock time (minutes) | | | |
```

---

### Step 3.9 — Draft Your Build Post

Structure your Build post (for LinkedIn, Esri Community, or a personal blog) using this outline. The GIS practitioner audience will respond to honesty about what failed and what improved.

```markdown
---
# Title: I Gave Claude an FME Workspace and Watched It Fail — Then I Fixed It

## Hook (2–3 sentences)
I've been using Claude Code CLI to automate FME workspace edits for [X months].
Last week Anthropic shipped an agent dashboard that finally showed me *where*
the agent was going wrong. Here's what I found.

## The Setup (1 paragraph)
[Describe your task: schema rename refactor, FME environment, what you expected]

## What the Dashboard Showed Me (the "before")
[Embed your session log screenshot]
[List your top 3 error patterns with specific examples]

> Example: "The agent invented a transformer called 'AttributeUpdater' in 4 of 
> 12 sessions. This transformer does not exist in FME. The workspace would 
> appear to build but fail at runtime."

## What I Changed in CLAUDE.md (the fix)
[Show the before/after CLAUDE.md diff — literally paste it, practitioners love this]

## What Improved (the "after")
[Embed your comparison table from Step 3.8]
[Quantify: "Transformer hallucinations dropped from 4/session to 0/session"]

## What the Dashboard Doesn't Do Yet
[Honest limitations you observed]

## Takeaway for GIS Practitioners
[One paragraph on why this matters for ETL supervision, not just software development]

## Resources
- Claude Code CLI: [link]
- Agent Dashboard video: https://www.youtube.com/watch?v=ZAaxx3qyT8g
- My CLAUDE.md template: [link to your gist or repo]
---
```

---

## 4. Validation

You've completed this exercise successfully when you can check off all of the following:

```
□ Claude Code dashboard is visible and showing step-level detail during a live session
□ Session 001 log is filled in with at least 5 observed steps
□ Error taxonomy has at least 3 populated categories
□ CLAUDE.md has at least 5 new lines added based on observed failures
□ Session 003 shows measurable improvement over Session 001 on at least 2 metrics
□ Build post draft exists with all 7 sections outlined
□ Your before/after comparison table is filled in
```

**Minimum success bar:** Even if Sessions 001 and 002 produce zero errors (lucky!), you still win — document what the agent did *correctly* and use that to reinforce your `CLAUDE.md` with positive examples. "Do it like you did in session 001, step 4" is also valid directive content.

---

## 5. Next Steps

### Immediate (this week)
- **Publish the Build post.** Don't wait for perfection. A draft with real data is worth 10x a polished post with generic advice.
- **Add your error taxonomy to a shared team doc** if you work with other GIS practitioners. Your pain is their pain.

### Short-term (next 2–4 weeks)
- **Wire the agent dashboard into your CI/CD pipeline.** If you're running Claude Code as part of an automated FME Flow trigger, the dashboard's error output should be captured to a log file and alert you on failures — not silently succeed.
- **Build a `CLAUDE.md` library.** You'll want different `CLAUDE.md` profiles for different task types: schema migrations, format conversions, coordinate system transformations. Start versioning them.

### Medium-term
- **Instrument your FME workspaces for AI readability.** Add structured comments in your `.fmw` files that give the agent anchor points: `# AGENT_READABLE: schema version 2.1 | last_modified: 2024-01-15`. This reduces the agent's need to reverse-engineer your intent.
- **Evaluate FME Flow's REST API as an agent tool.** Instead of the agent editing `.fmw` files directly, consider giving it authenticated access to FME Flow's REST API so it can submit jobs, read logs, and iterate — with the dashboard showing you every API call it makes.

### Watch & Verify
Re-watch the [source video](https://www.youtube.com/watch?v=ZAaxx3qyT8g) with this tutorial open. Fill in any gaps where I've marked **⚠️ Source gap** and update your own copy of this tutorial with the verified commands. That annotated version is itself worth sharing.

---

*Tutorial written for Daniel — GIS/AI practitioner. Grounded in Claude Code CLI established behavior; dashboard-specific commands flagged for verification against the source video.*