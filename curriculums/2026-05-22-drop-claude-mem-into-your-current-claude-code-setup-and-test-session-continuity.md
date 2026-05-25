# Drop `claude-mem` into Your Current Claude Code Setup and Test Session Continuity

*A hands-on tutorial for GIS/AI practitioners who are tired of re-explaining their FME workspace structure every single session.*

---

## 1. Introduction & Context

Every time you start a new Claude Code session, you're back to square one. You re-explain that your Sentinel Hub API calls use the Process API endpoint, not the older WMS-style interface. You re-describe your FME workspace naming conventions. You remind Claude which conda environment you're in and why you're pinned to a specific GDAL version. This is friction that compounds across dozens of sessions a week.

**`claude-mem`** is a persistent memory compression layer for Claude Code. It works by:

1. **Capturing** tool usage observations and conversation context as your sessions run
2. **Compressing** that context into semantic summaries using AI
3. **Injecting** the relevant summaries back into future sessions automatically

Crucially, it does this *without changing your existing stack*. You still use `claude` from the CLI exactly as you do now. The tool hooks into Claude Code's existing plugin/MCP infrastructure.

**Why this matters for your GIS work specifically:** Your sessions have unusually high setup cost. FME workspace topology, Sentinel Hub OAuth flows, coordinate reference system conventions, and Python geospatial environment quirks are all things Claude needs to understand before it can be genuinely useful — and right now you're paying that cost on every session. This one-week test will tell you whether `claude-mem` meaningfully reduces that overhead, and your actual session logs will be the evidence.

**Effort level:** Low. Installation is a single command. The experiment runs passively in the background.

---

## 2. Prerequisites

Before starting, confirm you have:

| Requirement | Why It's Needed |
|---|---|
| **Claude Code CLI** installed and working | `claude-mem` hooks directly into it |
| **Node.js ≥ 18.0.0** | `claude-mem` is an npm package requiring this minimum |
| **`npx` available** (comes with Node.js) | Used for the install command |
| **Active GIS project(s)** running through Claude Code | You need real sessions to test continuity against |
| **`ANTHROPIC_API_KEY` set** in your environment | Claude Code needs this; `claude-mem` uses the same SDK |

Check your Node version:

```bash
node --version
# Should output v18.0.0 or higher
```

Check Claude Code is working:

```bash
claude --version
```

> **Note:** If you're using conda environments for your Python geospatial work, make sure you have Node.js available in your base or system environment — you don't need it inside your geo conda env, just somewhere on your `PATH`.

---

## 3. Step-by-Step Guide

### Step 3.1 — Install `claude-mem`

Run the install command from any directory. You don't need to be inside a specific project:

```bash
npx claude-mem install
```

That's it. The installer auto-detects your Claude Code configuration directory and wires itself in as a plugin.

> **Alternative — install via the Claude Code plugin marketplace** (if you prefer keeping everything inside Claude Code):
> ```
> /plugin marketplace add thedotmack/claude-mem
> /plugin install claude-mem
> ```
> Run these commands inside an active Claude Code session.

### Step 3.2 — Restart Claude Code

The plugin won't be active in your current session. Fully exit and reopen:

```bash
# Exit any active claude session, then:
claude
```

On the first restart after install, there will be no prior memory to inject — that's expected. The system needs at least one completed session before it has anything to compress and restore.

### Step 3.3 — Prime Your First Session with GIS Context

This is the most important setup step. You want `claude-mem` to capture *rich, specific* context about your GIS environment. Don't be sparse — be explicit. Start a session and work through your actual tasks, but also deliberately surface the context that usually takes time to re-establish:

```bash
claude
```

Once inside, work through your projects naturally. To ensure `claude-mem` captures the right things, weave in context-establishing statements as you work:

```
I'm working in the sentinel-hub-pipeline conda environment. 
Key packages: sentinelhub==3.9.x, geopandas, rasterio, GDAL 3.6.4.

My FME workspace structure:
- /workspaces/sentinel_ingest/   → raw Scene processing workbenches  
- /workspaces/analysis/          → derived product workbenches
- /workspaces/shared/            → custom transformers used across both

The Sentinel Hub Process API endpoint I always use is:
https://services.sentinel-hub.com/api/v1/process

Auth is OAuth2 client credentials, tokens cached at ~/.sentinelhub/token_cache
```

Then do actual work. Let Claude use tools — read files, write code, run commands. The tool-usage observations are a key part of what `claude-mem` captures.

### Step 3.4 — Set Up a Session Log File

You'll want raw evidence for your write-up. Keep a simple log file for the week. Create it now:

```bash
mkdir -p ~/claude-mem-experiment
cat > ~/claude-mem-experiment/session_log.md << 'EOF'
# claude-mem GIS Session Log

## Experiment Start Date: [TODAY]

## What I'm Testing
- FME workspace structure continuity
- Sentinel Hub API pattern recall
- Python environment (conda env name, package versions, GDAL)
- CRS / projection conventions
- Any other GIS-specific context

---

## Sessions

EOF
```

After each Claude Code session, append a brief entry:

```bash
cat >> ~/claude-mem-experiment/session_log.md << 'EOF'

### Session [DATE] [TIME]
**Context injected at start?** [Yes/No]
**What it got right:**
- 

**What it got wrong or missed:**
- 

**Surprising behavior:**
- 

---
EOF
```

### Step 3.5 — Run Sessions Across the Week

Run your normal GIS workload through Claude Code for 7 days. Here's a structured test plan targeting your specific domain:

#### Day 1–2: Baseline Establishment
Work through real tasks. Don't do anything special except logging. The goal is populating memory with authentic context.

#### Day 3–4: Test FME Workspace Continuity
Start a fresh session. *Without re-explaining anything*, ask:

```
What do you remember about my FME workspace structure?
```

Log exactly what Claude reports. Then ask:

```
Which workbench directory would I put a new transformer 
that processes Sentinel-2 L2A scenes before analysis?
```

A good memory restoration should get this right from prior context.

#### Day 5: Test Sentinel Hub API Pattern Recall

Start a fresh session and immediately ask:

```
Write me a minimal Python snippet to request a 
True Color composite from Sentinel Hub — use the 
API patterns from our previous sessions.
```

Log whether it uses the Process API endpoint correctly, whether it references your OAuth token cache location, and whether it uses the right Python environment's package versions.

#### Day 6: Test Python Environment Recall

Start a fresh session and ask:

```
Which conda environment should I activate for our 
Sentinel Hub pipeline work, and what GDAL version 
are we pinned to?
```

#### Day 7: Stress Test

Intentionally start a session with a context-heavy task that *requires* prior knowledge to do correctly:

```
Continue the Sentinel Hub ingestion pipeline 
we were working on. Pick up where we left off.
```

Document whether it can orient itself or whether it's lost.

### Step 3.6 — Capture Raw Session Logs as Evidence

Before closing each Claude Code session, copy the conversation to your log directory. If your terminal supports it:

```bash
# Save terminal scrollback to file (adjust for your terminal emulator)
# Most straightforward: use script(1) to record sessions going forward

# Start a recorded session:
script ~/claude-mem-experiment/session_$(date +%Y%m%d_%H%M).txt
claude
# ... do your work ...
exit  # ends the script recording
```

Or, within Claude Code, ask Claude to summarize what it remembers at the start and end of each session, then copy that output manually.

---

## 4. Validation

### How to Confirm `claude-mem` Is Actually Running

At the start of any session after Day 1, you should see injected context. You can verify the plugin loaded by checking whether Claude Code acknowledges prior session context at startup. If you're unsure, ask directly inside a session:

```
Are you loading any persistent memory context from previous sessions?
What context do you have about my current GIS projects?
```

If `claude-mem` is working, Claude should respond with compressed summaries of prior sessions — not a blank "I don't have context from previous conversations."

### Scoring Your One-Week Test

At the end of Day 7, evaluate against these criteria:

| Test | Pass Condition |
|---|---|
| **FME workspace structure** | Claude correctly names your workspace directories without being told |
| **Sentinel Hub endpoint** | Claude uses `https://services.sentinel-hub.com/api/v1/process` unprompted |
| **Auth pattern** | Claude references OAuth2 client credentials (even if not the token path) |
| **Conda environment** | Claude recalls the env name without prompting |
| **GDAL version** | Claude recalls the pinned version |
| **Cross-session continuity** | At least 3 of 7 sessions show meaningful injected context |

### Review Your Log for The Build Post

Your `~/claude-mem-experiment/session_log.md` file is your source material. Look for:

- **Concrete wins**: verbatim quotes from Claude demonstrating recalled context
- **Concrete failures**: cases where it hallucinated a detail or missed key context entirely
- **Surprising behaviors**: things it remembered that you didn't expect, or forgot that you did

---

## 5. Next Steps

### Write the Build Post

Your post structure, based on what the experiment will produce:

```markdown
## Title: Does claude-mem Actually Remember My GIS Stack?

### Setup (2 sentences)
### What I tested (bullet list)
### Session log evidence (3–4 verbatim excerpts)
### What it got right (scored against the table above)
### What it got wrong (be specific — this is the useful part)
### Verdict: Is the friction reduction worth it?
```

Include at least one raw session log excerpt. The specificity of "it correctly recalled my FME workspace structure but hallucinated the GDAL version as 3.6.3 instead of 3.6.4" is far more useful to your readers than a general impression.

### If It Works Well — Go Deeper

> **Note:** The source repository documents these directions, but specific configuration flags beyond those shown above should be verified against the [full README](https://github.com/thedotmack/claude-mem) before relying on them, as the fetched source was truncated.

- Explore whether `claude-mem` exposes MCP search tools for querying your compressed session history directly
- Test whether the memory survives across machines if you're working across a desktop and a remote compute environment
- Evaluate whether project-specific memory isolation is possible (keeping your Sentinel Hub context separate from unrelated work)

### If It Doesn't Work Well — Document the Gaps

Negative results are just as publishable. If `claude-mem` fails to reliably restore your GIS context, document *why*:

- Is the compression too lossy for domain-specific technical details?
- Is the context injection happening but Claude Code ignoring it?
- Are your sessions too long/complex for effective compression?

These are genuinely useful findings for the broader Claude Code user community.

### Adjacent Experiments to Run Next

Once you have a baseline from this experiment:

1. **Combine with a project-level `CLAUDE.md`**: Put your FME workspace conventions and Sentinel Hub patterns in a `CLAUDE.md` file at the root of your GIS project directory. Test whether `claude-mem` + `CLAUDE.md` gives better continuity than either alone.
2. **Test with Gemini CLI**: `claude-mem` supports Gemini CLI via `npx claude-mem install --ide gemini-cli` — useful if you want to compare memory behavior across AI coding assistants.
3. **Evaluate for team use**: If you work with other practitioners on shared GIS pipelines, test whether `claude-mem`'s compressed context is useful as onboarding material — what does it "know" about a project after a week of active use?

---

*Based on the `thedotmack/claude-mem` repository (v6.5.0). All commands verified against the project's source content. Configuration options beyond those explicitly documented in the source should be confirmed against the [live README](https://github.com/thedotmack/claude-mem) before use.*