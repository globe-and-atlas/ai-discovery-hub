# Wire the Claude Code Agent Dashboard into Your FME Debug Loop

## A Hands-On Tutorial for Visualizing Multi-Agent Workspace Generation

---

## 1. Introduction & Context

### What Is This?

Claude Code recently shipped an **Agent Dashboard** — a visual, real-time interface that lets you watch your Claude Code CLI agent as it thinks, selects tools, executes sub-tasks, and transitions between states. Instead of staring at a scrolling terminal wall of text and hoping something meaningful emerges, the dashboard gives you a structured, inspectable view of every decision your agent makes.

For FME power users who are already using Claude Code CLI to generate, debug, or modify FME workspaces programmatically, this is a significant upgrade to your development loop.

### Why Does This Matter for FME Work?

When you run a script that asks Claude Code to generate an FME workspace (`.fmw` file), route data between transformers, or debug a failing translation, a lot happens invisibly:

- Which tools did the agent call, and in what order?
- Did it read the wrong source schema before writing the workspace?
- Where did it stall or hallucinate a transformer name?
- What intermediate XML did it produce before committing to a file?

Previously, you had to infer this from log output — or instrument your own debugging. The Agent Dashboard makes **all of this visible without extra code**.

### The Core Learning Outcome

By the end of this tutorial, you will have:

1. Enabled and launched the Claude Code Agent Dashboard
2. Run an existing FME workspace generation script as a monitored agent task
3. Read and documented the tool call graph and intermediate states the dashboard exposes
4. Built a repeatable debug habit you can apply to every future FME agent run

---

## 2. Prerequisites

Before starting, confirm the following are in place:

### Tools & Versions

| Requirement | Minimum Version | How to Check |
|---|---|---|
| Claude Code CLI | Latest (post Agent Dashboard release) | `claude --version` |
| Node.js | 18+ | `node --version` |
| FME Desktop or FME Flow | 2023.x or later | FME Help → About |
| A shell environment | bash / zsh / PowerShell | — |
| An Anthropic API key | Active, with Claude Sonnet/Opus access | Anthropic Console |

### Knowledge Assumptions

- You have **at least one existing Claude Code script** that generates or modifies an FME workspace (`.fmw`) file. If you don't have one yet, the tutorial includes a minimal starter script in Step 3.
- You are comfortable running CLI commands and reading JSON or XML output.
- You understand the basic structure of an FME workspace (readers, writers, transformers in an XML-based `.fmw` format).

### Install / Update Claude Code CLI

```bash
# Install globally if not already present
npm install -g @anthropic-ai/claude-code

# Or update to latest
npm update -g @anthropic-ai/claude-code

# Confirm version (should show Agent Dashboard support)
claude --version
```

---

## 3. Step-by-Step Guide

### Step 3.1 — Understand the Agent Dashboard Architecture

Before touching any configuration, understand what you're enabling:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Terminal                         │
│  claude --agent-dashboard run fme_generator.md          │
└────────────────────────┬────────────────────────────────┘
                         │ spawns
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Claude Code Agent Runtime                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Planning │→ │Tool Calls│→ │ State / Memory Layer  │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ streams events to
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Dashboard (localhost:PORT)            │
│  • Tool call timeline                                    │
│  • Intermediate state inspector                         │
│  • Token usage per step                                 │
│  • Sub-agent spawn graph (for multi-agent setups)       │
└─────────────────────────────────────────────────────────┘
```

The dashboard is a **local web server** that Claude Code spins up alongside your agent run. It does not send additional data to Anthropic — it reads the same event stream your terminal already receives.

---

### Step 3.2 — Enable the Agent Dashboard Flag

The dashboard is activated via a CLI flag or a configuration entry in your project's `claude.json`.

**Option A: Per-run flag (recommended for first-time use)**

```bash
claude run --agent-dashboard your_task.md
```

**Option B: Project-level config (recommended for ongoing FME work)**

Create or edit `.claude/claude.json` at the root of your FME project directory:

```json
{
  "version": "1",
  "agentDashboard": {
    "enabled": true,
    "port": 7842,
    "autoOpen": true,
    "retainHistory": true
  },
  "model": "claude-sonnet-4-5",
  "tools": {
    "fileRead": true,
    "fileWrite": true,
    "bash": true
  }
}
```

> **Port Note:** `7842` is arbitrary. Pick any available port. `autoOpen: true` will launch your default browser to `http://localhost:7842` when the agent starts.

---

### Step 3.3 — Prepare Your FME Task File

Claude Code agents work best with a well-structured **task prompt file** (Markdown). If you already have one, adapt it. If not, here is a minimal but realistic starter:

Create `fme_workspace_generator.md` in your project root:

````markdown
# Task: Generate an FME Workspace for CSV to GeoJSON Translation

## Objective
Create a valid FME workspace file (`output/csv_to_geojson.fmw`) that:
1. Reads from `data/input/locations.csv` (columns: id, name, latitude, longitude)
2. Reprojects coordinates from WGS84 (EPSG:4326) — no reprojection needed, keep native
3. Writes to `output/locations.geojson` using the GeoJSON writer
4. Includes a `StringConcatenator` transformer to merge `id` and `name` into a `label` attribute

## Constraints
- Use FME 2023 XML workspace format
- Transformer GUIDs must be unique UUIDs
- All file paths should be relative to the workspace location
- Do not include any FME Flow-specific directives

## Steps You Should Follow
1. Read and validate the schema of `data/input/locations.csv`
2. Draft the reader block XML
3. Draft the transformer block XML
4. Draft the writer block XML
5. Assemble and write the final `.fmw` file
6. Validate the XML is well-formed

## Output
Write the completed workspace to: `output/csv_to_geojson.fmw`
Log each major step to: `output/generation_log.txt`
````

Create the supporting input file `data/input/locations.csv`:

```csv
id,name,latitude,longitude
1,Central Park,40.785091,-73.968285
2,Golden Gate Bridge,37.819929,-122.478255
3,Space Needle,47.620499,-122.349274
```

Create output directory:

```bash
mkdir -p output
```

---

### Step 3.4 — Launch the Agent with the Dashboard

Run the agent. Watch for the dashboard URL in your terminal output:

```bash
claude run --agent-dashboard fme_workspace_generator.md
```

**Expected terminal output (first few lines):**

```
Claude Code v1.x.x
Agent Dashboard: http://localhost:7842
  → Opening in browser...

[Agent] Starting task: Generate an FME Workspace for CSV to GeoJSON Translation
[Tool]  bash → ls data/input/
[Tool]  file_read → data/input/locations.csv
[Agent] Planning workspace structure...
```

If the browser doesn't open automatically:

```bash
# macOS
open http://localhost:7842

# Linux
xdg-open http://localhost:7842

# Windows
start http://localhost:7842
```

---

### Step 3.5 — Navigate the Agent Dashboard UI

Once the dashboard loads, you'll see several panels. Here's what each one means for your FME debug workflow:

#### Panel 1: Tool Call Timeline

```
Timeline View
─────────────────────────────────────────────────────────
00:00  [bash]         ls data/input/               ✓ 12ms
00:01  [file_read]    data/input/locations.csv     ✓ 8ms
00:03  [think]        Planning XML structure...    ✓ 2.1s
00:05  [file_write]   output/generation_log.txt    ✓ 15ms
00:07  [file_write]   output/csv_to_geojson.fmw    ✓ 22ms
00:08  [bash]         xmllint --noout output/...   ✓ 45ms
─────────────────────────────────────────────────────────
```

**What to look for:**
- Any tool call marked `✗` (failed) — click it to see the error and the agent's recovery attempt
- Long `[think]` durations — this is where the agent is reasoning; a very long think often precedes a hallucination
- Unexpected `[file_read]` calls — did the agent read files you didn't intend?

#### Panel 2: State Inspector (click any tool call row)

Clicking a `[file_write]` row expands to show:

```json
{
  "tool": "file_write",
  "input": {
    "path": "output/csv_to_geojson.fmw",
    "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<FMETemplate..."
  },
  "output": {
    "success": true,
    "bytes_written": 4821
  },
  "tokens_used": {
    "input": 2847,
    "output": 1203
  }
}
```

**This is the key FME insight:** You can now read the *exact XML* the agent wrote at each intermediate step — before it was committed to disk. If the final `.fmw` is invalid, scroll back through write events to find where the XML first broke.

#### Panel 3: Agent Reasoning Log

This shows the chain-of-thought text between tool calls:

```
[Agent Reasoning @ 00:03]
I need to construct the FMETemplate XML. The CSV reader block requires:
- DATASET directive pointing to locations.csv
- Feature type definition with columns: id, name, latitude, longitude

I'll use the StringConcatenator transformer. Its XML block needs:
- A unique GUID for the transformer node
- INPUT_PORT and OUTPUT_PORT definitions
- The expression: @Value(id) + " - " + @Value(name)

Let me draft the transformer block first, then assemble...
```

**FME-specific value:** This reveals whether the agent correctly understands FME transformer semantics (e.g., `@Value()` syntax) or is making educated guesses that will produce invalid XML.

#### Panel 4: Token Budget Tracker

```
Token Usage
────────────────────────────────
Context window:  200,000 tokens
Used so far:      12,847 tokens  (6.4%)
Estimated finish: ~18,000 tokens
────────────────────────────────
```

For large FME workspaces (hundreds of transformers), this helps you predict whether a single agent run will fit in context or needs to be broken into sub-tasks.

---

### Step 3.6 — Run the Agent and Actively Monitor

Don't just let the agent run unattended. Practice **active monitoring**:

1. **Watch the first 3 tool calls.** Did the agent read your CSV before trying to write the workspace? If it skips straight to writing, that's a red flag — it's generating from assumptions, not your actual schema.

2. **Pause and inspect at `[think]` events.** The dashboard should let you see the reasoning text in real time. If you see the agent reasoning about transformer names that don't exist in FME (e.g., `CSVToGeoJSON` as a single transformer — which isn't real), you'll know to intervene or add constraints to your task file.

3. **Check the XML mid-write.** If the agent writes the file in chunks or rewrites it, each write event is capturable. Compare intermediate versions to understand how the workspace evolved.

4. **Note any `[bash]` validation calls.** If your task included "validate the XML is well-formed," the dashboard will show whether the `xmllint` call succeeded and what the agent did if it failed.

---

### Step 3.7 — Document What the Dashboard Reveals

This is the most important step for building long-term value. Open a new file called `dashboard_findings.md` and fill it in as you watch:

```markdown
# Agent Dashboard Findings — FME CSV to GeoJSON Run
Date: [today]
Task file: fme_workspace_generator.md

## Tool Call Sequence (Actual)
1. bash → ls data/input/
2. file_read → data/input/locations.csv
3. [think] → 2.1 seconds of planning
4. file_write → output/generation_log.txt
5. file_write → output/csv_to_geojson.fmw
6. bash → xmllint validation

## What Was Previously Invisible
- [ ] The agent read the CSV *before* writing (good — schema-grounded)
- [ ] The think step lasted 2.1s — it was reasoning about GUID generation
- [ ] First write attempt used a hardcoded GUID; second write corrected it
- [ ] The StringConcatenator expression used @Value() correctly

## Surprises / Anomalies
- The agent made an unexpected file_read call on `.claude/claude.json`
  → Appears to be checking tool permissions. Not a bug, just invisible before.

## Failures Caught by Dashboard
- None on this run. (Document any `✗` events here on future runs)

## Recommended Task File Changes
- Add explicit instruction: "Generate UUIDs using Python's uuid module via bash"
  → Dashboard showed the agent was manually constructing UUID strings (fragile)
```

---

### Step 3.8 — Iterate: Run a Deliberately Broken Task

To see the dashboard's real debugging value, introduce a known error and watch how the agent handles it.

Edit `fme_workspace_generator.md` and add a bad constraint:

```markdown
## Additional Constraint (INTENTIONAL ERROR FOR TESTING)
- Use the transformer named `LatLongToGeoPoint` to convert coordinates
  (Note: this transformer does not exist in FME — use `VertexCreator` instead)
```

Re-run:

```bash
claude run --agent-dashboard fme_workspace_generator.md
```

In the dashboard, watch for:

- Does the agent use `LatLongToGeoPoint` verbatim (hallucination risk)?
- Does it pause in a `[think]` block and reason about whether the transformer is valid?
- Does it attempt a `[bash]` call to verify transformer existence?
- Does it fall back to `VertexCreator` on its own?

**Document this behavior in `dashboard_findings.md`** — it tells you exactly how much FME domain knowledge is baked into the model vs. how much you need to scaffold with explicit instructions.

---

## 4. Validation

### Checklist: Did You Complete the Exercise?

Work through each item and mark it done:

```
[ ] 1. `claude --version` shows a version that supports --agent-dashboard flag
[ ] 2. `.claude/claude.json` created with agentDashboard config block
[ ] 3. `fme_workspace_generator.md` task file created with FME-specific steps
[ ] 4. Agent ran successfully and dashboard opened in browser
[ ] 5. Tool call timeline is visible and shows ≥4 distinct tool calls
[ ] 6. Clicked at least one tool call row and inspected its input/output JSON
[ ] 7. Read the agent reasoning text from at least one [think] event
[ ] 8. `output/csv_to_geojson.fmw` file exists and is valid XML
[ ] 9. Ran the broken-constraint test and documented the agent's behavior
[  ] 10. `dashboard_findings.md` is filled in with at least 3 observations
```

### Functional Validation of the FMW Output

```bash
# Validate the workspace XML is well-formed
xmllint --noout output/csv_to_geojson.fmw
# → No output = valid XML

# Check for required FME elements
grep -c "FMETemplate" output/csv_to_geojson.fmw
# → Should return 1

grep -c "StringConcatenator" output/csv_to_geojson.fmw
# → Should return ≥ 1

# Inspect the full file
cat output/csv_to_geojson.fmw
```

### Dashboard Validation

If the dashboard is working correctly:

- **URL is accessible:** `http://localhost:7842` loads without error
- **Timeline populated:** You see at least one entry per bullet point in your task file's "Steps You Should Follow" section
- **State inspector works:** Clicking a row shows a JSON payload with `tool`, `input`, and `output` keys
- **History retained:** After the run completes, the dashboard still shows all events (because `retainHistory: true`)

---

## 5. Next Steps

You've wired the Agent Dashboard into one FME script. Here's how to build on that foundation:

### Immediate (This Week)

**5.1 Add the Dashboard to Your 3-Layer Agent Architecture**

If your FME automation uses a planner → executor → validator pattern, the dashboard will show each layer as a distinct event cluster. Tag your task files with layer labels:

```markdown
## Agent Layer: EXECUTOR
## Parent Task ID: planner_run_20240115
```

This makes the dashboard timeline readable across complex multi-agent runs.

**5.2 Create a Dashboard Review Ritual**

After every agent-generated FME workspace, spend 5 minutes in the dashboard before opening the workspace in FME. Ask:
- Did the agent read what I expected?
- Were there any failed tool calls it recovered silently?
- How many tokens did this use? Is it trending up (growing complexity)?

### Short-Term (Next 2 Weeks)

**5.3 Build a Tool Call Assertion Library**

Based on your `dashboard_findings.md` patterns, create a set of expected tool call sequences for common FME tasks:

```markdown
# Expected Tool Call Pattern: Schema-First Workspace Generation
1. file_read (CSV/source data)
2. think (schema analysis)
3. file_write (draft workspace)
4. bash (xmllint validation)
5. [optional] file_write (correction if xmllint failed)
```

If a run deviates from this pattern, the dashboard makes it immediately visible.

**5.4 Export Dashboard Events for Logging**

Check if your Claude Code version supports event export:

```bash
claude run --agent-dashboard --export-events output/agent_events.jsonl fme_workspace_generator.md
```

This JSONL file becomes a machine-readable audit trail you can query later:

```bash
# How many tool calls per run?
cat output/agent_events.jsonl | jq 'select(.type == "tool_call")' | wc -l

# Which files were read?
cat output/agent_events.jsonl | jq 'select(.tool == "file_read") | .input.path'
```

### Long-Term (Next Month)

**5.5 Use Dashboard Data to Fine-Tune Your Task Files**

After 10+ runs, you'll have patterns in your `dashboard_findings.md` documents. Use these to iteratively improve your task file templates:
- Add explicit instructions where the agent consistently uses [think] time unnecessarily
- Remove instructions where the agent consistently does the right thing without prompting
- Identify which FME transformer names the agent gets wrong and add a reference block to your task files

**5.6 Integrate Dashboard Monitoring into Your CI/CD Loop**

For automated FME workspace generation (e.g., triggered by schema changes), set up headless dashboard logging:

```bash
# Headless run with event export — no browser
claude run \
  --agent-dashboard \
  --no-browser \
  --export-events logs/events_$(date +%Y%m%d_%H%M%S).jsonl \
  fme_workspace_generator.md
```

Build a simple script that checks the JSONL for failed tool calls and alerts you:

```python
# check_agent_run.py
import json, sys

events_file = sys.argv[1]
failures = []

with open(events_file) as f:
    for line in f:
        event = json.loads(line)
        if event.get("type") == "tool_call" and not event.get("output", {}).get("success", True):
            failures.append(event)

if failures:
    print(f"ALERT: {len(failures)} failed tool calls detected")
    for f in failures:
        print(f"  - {f['tool']} on {f['input'].get('path', '?')}: {f['output'].get('error')}")
    sys.exit(1)
else:
    print("All tool calls succeeded.")
    sys.exit(0)
```

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│           Claude Code Agent Dashboard — FME Cheat Sheet      │
├──────────────────────────────────────────────────────────────┤
│ Enable dashboard:  claude run --agent-dashboard task.md      │
│ Config location:   .claude/claude.json                       │
│ Default port:      7842 (configurable)                       │
│ Dashboard URL:     http://localhost:7842                      │
├──────────────────────────────────────────────────────────────┤
│ What to watch for in FME tasks:                              │
│  ✓ file_read before file_write (schema-grounded)            │
│  ✗ Skips straight to file_write (assumption-based)          │
│  ✓ bash xmllint call after workspace write                  │
│  ✗ No validation step                                       │
│  ✓ think time < 3s per step                                 │
│  ⚠ think time > 5s (may indicate uncertainty/hallucination) │
├──────────────────────────────────────────────────────────────┤
│ Key files to create:                                         │
│  fme_workspace_generator.md   → task prompt                 │
│  .claude/claude.json          → dashboard config             │
│  dashboard_findings.md        → your observations            │
└──────────────────────────────────────────────────────────────┘
```

---

*Tutorial complete. The goal was not just to turn on a dashboard — it was to build the habit of treating your agent's internal process as a debuggable system. Every `[think]` block is a line of reasoning you can now read. Every tool call is a decision you can now audit. Your FME debug loop just got a new first step.*