# Add `claude-mem` Persistence to Your Sentinel Hub Scripting Sessions

## A Hands-On Curriculum for GIS Practitioners Using Claude Code CLI

---

## 1. Introduction & Context

### The Problem: Every Session Starts Blind

If you've used **Claude Code CLI** for Sentinel Hub API scripting, you've experienced the friction firsthand. Every new session, you re-explain:

- Your Sentinel Hub instance ID and preferred endpoint patterns
- Which EvalScript conventions you follow (band normalization, output formats)
- Your project's coordinate reference systems and AOI definitions
- Past mistakes Claude already helped you fix — and shouldn't repeat

This is the **stateless memory problem**. Claude is powerful, but without cross-session context, you're constantly re-onboarding your AI assistant.

### The Solution: `claude-mem`

[`claude-mem`](https://github.com/thedotmack/claude-mem) is a lightweight persistence layer that:

1. **Captures** what your Claude agent does across sessions
2. **Compresses** that history using AI summarization
3. **Injects** relevant context back into future sessions automatically

For GIS practitioners doing iterative Sentinel Hub scripting — tuning EvalScripts, debugging API calls, refining cloud-masking logic — this means Claude remembers your conventions, your errors, and your progress.

### Why This Exercise Matters

This exercise has a concrete, measurable goal: **reduce correction prompts by 30% or more** across three Sentinel Hub scripting sessions. You'll instrument, measure, and evaluate — and if it works, you'll document a replicable setup for other GIS practitioners.

---

## 2. Prerequisites

### Required Knowledge

- Basic familiarity with the **Sentinel Hub API** (Process API, EvalScripts, BYOC)
- Comfort using a **terminal / shell** (bash, zsh, or PowerShell)
- Basic **Python** (for scripting sessions) or JavaScript (for EvalScripts)
- Understanding of what **Claude Code CLI** is and how to invoke it

### Required Software & Accounts

| Requirement | Version / Notes |
|---|---|
| Node.js | v18+ (for `claude-mem`) |
| npm or npx | Comes with Node.js |
| Claude Code CLI | Latest — [install guide](https://docs.anthropic.com/en/docs/claude-code) |
| Python | 3.9+ |
| Sentinel Hub account | Free trial acceptable — [sentinel-hub.com](https://www.sentinel-hub.com/) |
| `sentinelhub-py` library | `pip install sentinelhub` |
| A text editor | VS Code recommended |

### Pre-Exercise Setup Checklist

Before starting the timed sessions, confirm:

```bash
# Verify Claude Code CLI
claude --version

# Verify Node.js
node --version   # Should show v18+

# Verify Python environment
python --version
pip show sentinelhub

# Verify Sentinel Hub credentials are accessible
echo $SH_CLIENT_ID
echo $SH_CLIENT_SECRET
echo $SH_INSTANCE_ID
```

If any of these fail, resolve them before continuing.

---

## 3. Step-by-Step Guide

### Phase 0: Baseline Measurement (Before `claude-mem`)

Before installing `claude-mem`, you need a **baseline**. This is what makes the 30% improvement claim measurable.

#### 0.1 Define What You're Measuring

A **"correction prompt"** is any follow-up message you send because Claude:
- Forgot your project's CRS or AOI
- Repeated a mistake you already corrected
- Asked you to re-explain Sentinel Hub auth patterns
- Generated code inconsistent with conventions you've established

Create a simple tally sheet:

```markdown
# Session Correction Tally

## Session 1 (Baseline — No claude-mem)
- Correction prompts: ___
- Total prompts: ___
- Correction ratio: ___

## Session 2 (With claude-mem)
- Correction prompts: ___
- Total prompts: ___
- Correction ratio: ___

## Session 3 (With claude-mem, mature memory)
- Correction prompts: ___
- Total prompts: ___
- Correction ratio: ___
```

Save this as `~/sentinel-claudemem-eval/tally.md`.

#### 0.2 Run Your Baseline Session (Session 1)

Pick a **real scripting task** you'd normally do. Suggested tasks that generate natural correction opportunities:

> **Task for Session 1:** Write a Python script using `sentinelhub-py` that fetches a True Color (B04, B03, B02) Sentinel-2 image for a custom AOI, saves it as a GeoTIFF, and applies a basic cloud mask using the CLM band.

Open Claude Code CLI without any memory tooling:

```bash
# Start a fresh session — no memory injection
claude
```

Work through the task naturally. **Tally every correction prompt honestly.** When done:

```bash
# Note your totals in tally.md
# Example:
# Session 1: 7 correction prompts / 22 total prompts = 31.8% correction ratio
```

---

### Phase 1: Install and Configure `claude-mem`

#### 1.1 Install `claude-mem`

```bash
# Install globally via npm
npm install -g claude-mem

# Verify installation
claude-mem --version
```

If you prefer not to install globally, use `npx`:

```bash
npx claude-mem --version
```

#### 1.2 Initialize `claude-mem` for Your Project

Create a dedicated directory for your Sentinel Hub work:

```bash
mkdir -p ~/sentinel-claudemem-eval
cd ~/sentinel-claudemem-eval

# Initialize claude-mem in this directory
claude-mem init
```

This creates a `.claude-mem/` directory with:
```
.claude-mem/
├── config.json        # Configuration
├── sessions/          # Raw session logs
└── memory.md          # Compressed, injectable memory
```

#### 1.3 Review and Customize Configuration

Open `.claude-mem/config.json`:

```json
{
  "projectName": "sentinel-hub-scripting",
  "compressionModel": "claude-haiku-4-5",
  "maxMemoryTokens": 2000,
  "autoInject": true,
  "sessionLogPath": "./sessions",
  "memoryPath": "./memory.md"
}
```

**Recommended customizations for Sentinel Hub work:**

```json
{
  "projectName": "sentinel-hub-gis-scripting",
  "compressionModel": "claude-haiku-4-5",
  "maxMemoryTokens": 2500,
  "autoInject": true,
  "sessionLogPath": "./.claude-mem/sessions",
  "memoryPath": "./.claude-mem/memory.md",
  "contextHints": [
    "Sentinel Hub API",
    "EvalScript",
    "sentinelhub-py",
    "GeoTIFF",
    "cloud masking"
  ]
}
```

Save the file.

#### 1.4 Seed Initial Memory (Critical Step)

Before your first `claude-mem`-assisted session, manually seed the memory file with your project conventions. This front-loads the context that you'd otherwise re-explain:

```bash
# Create your initial memory seed
cat > .claude-mem/memory.md << 'EOF'
# Sentinel Hub Scripting — Project Memory

## Project Conventions

### Sentinel Hub Configuration
- Instance ID: stored in env var $SH_INSTANCE_ID
- Auth: OAuth2 via $SH_CLIENT_ID / $SH_CLIENT_SECRET
- Primary endpoint: https://services.sentinel-hub.com
- Preferred library: sentinelhub-py (Python)

### Coordinate Reference Systems
- Default CRS: EPSG:4326 for API calls, EPSG:32633 for local processing
- AOI format: GeoJSON FeatureCollection or bbox [minLon, minLat, maxLon, maxLat]

### EvalScript Conventions
- Output format: FLOAT32 for analysis, UINT8 for visualization
- Band order: always document in comments at top of EvalScript
- Cloud masking: use CLM band where available; threshold SCL values 8,9,10 for L2A
- Normalization: divide by 10000 for reflectance values

### Code Conventions
- All scripts use Python 3.9+
- Dependencies: sentinelhub, numpy, rasterio, geopandas
- Output files: GeoTIFF with CRS embedded, named pattern: {satellite}_{date}_{band}_{aoi}.tif
- Error handling: always wrap API calls in try/except with sentinelhub-specific exceptions

### Known Issues Resolved
- (Will populate after Session 1)

## Session History
- (Will populate after sessions)
EOF
```

---

### Phase 2: Scripting Sessions with `claude-mem`

#### 2.1 Session 2 — First `claude-mem`-Assisted Session

**Task for Session 2:** Extend your Session 1 script to support multi-temporal image fetching — retrieve Sentinel-2 True Color images for the same AOI across a date range (e.g., monthly composites for a full year), and generate a simple change detection output.

**Starting the session with memory injection:**

```bash
cd ~/sentinel-claudemem-eval

# Start Claude Code with memory injection
claude-mem start -- claude
```

What happens here:
1. `claude-mem` reads `.claude-mem/memory.md`
2. Prepends it as context to your Claude Code session
3. Logs everything that happens during the session
4. Compresses and updates memory when the session ends

**Alternatively, inject memory manually into your first prompt:**

```bash
# Generate the injection snippet
claude-mem inject

# This outputs something like:
# --- INJECTED CONTEXT (claude-mem) ---
# [Your memory.md contents]
# --- END INJECTED CONTEXT ---
```

Copy this into your first message to Claude, then proceed with your task.

**During Session 2 — track your tally:**

```
Keep your tally.md open in a split window.
Mark a tally every time you send a correction prompt.
Note: did Claude AVOID repeating Session 1 mistakes?
```

**After Session 2 — save the session:**

```bash
# claude-mem automatically logs if started with 'claude-mem start'
# If manual, save your session transcript
claude-mem save --session "session-2-multitemporal"

# Compress and update memory
claude-mem compress
```

Inspect the updated memory:

```bash
cat .claude-mem/memory.md
```

You should see new entries like:
```markdown
## Session History

### Session 2 — Multi-temporal fetching (2024-01-XX)
- Implemented date range iteration with SentinelHubRequest
- Resolved: dateutil parser conflict with sentinelhub internal dates
- Established pattern: use datetime objects, not strings, for time_interval
- Output naming convention confirmed: S2L2A_YYYYMMDD_TrueColor_{aoi}.tif
```

#### 2.2 Session 3 — Mature Memory Test

**Task for Session 3:** Refactor Sessions 1 and 2's scripts into a reusable `SentinelProcessor` class with methods for single-image fetch, multi-temporal fetch, and cloud-masked composite generation. Add a CLI interface using `argparse`.

This session is the real test. Claude should now:
- Know your CRS conventions without being told
- Know your file naming patterns
- Know which errors were already resolved
- Know your dependency stack

```bash
cd ~/sentinel-claudemem-eval

# Start with accumulated memory
claude-mem start -- claude
```

**Track corrections the same way.** Pay special attention to whether Claude proactively applies conventions from memory without prompting.

After Session 3:

```bash
claude-mem save --session "session-3-refactor"
claude-mem compress
```

---

### Phase 3: Measure and Evaluate

#### 3.1 Calculate Your Correction Ratios

Fill in your tally sheet:

```markdown
# Results

## Session 1 (Baseline — No claude-mem)
- Correction prompts: [X]
- Total prompts: [Y]  
- Correction ratio: [X/Y × 100]%

## Session 2 (With claude-mem, seeded memory)
- Correction prompts: [X]
- Total prompts: [Y]
- Correction ratio: [X/Y × 100]%
- Change from baseline: [±%]

## Session 3 (With claude-mem, accumulated memory)
- Correction prompts: [X]
- Total prompts: [Y]
- Correction ratio: [X/Y × 100]%
- Change from baseline: [±%]

## Verdict
- Did claude-mem reduce friction by ≥30%? YES / NO
- Average correction ratio with claude-mem: [%]
- Reduction from baseline: [%]
```

#### 3.2 Interpreting Results

| Outcome | Interpretation |
|---|---|
| ≥30% reduction | Strong signal — document for Tool Critic post |
| 15–29% reduction | Moderate — note setup quality; retry with better seed |
| <15% reduction | Weak — check if memory is actually injecting; review config |
| No reduction | Diagnose: is `claude-mem inject` running? Is memory.md populated? |

**Common reasons for poor results:**
- Memory file not injecting (run `claude-mem inject` and verify output)
- Seed memory too generic (add more project-specific conventions)
- Tasks too different across sessions (correction prompts are domain-shift noise)
- `maxMemoryTokens` too low — increase to 3000+

---

### Phase 4: Document for the Tool Critic Post (If 30%+ Achieved)

If you hit the threshold, you've earned the documentation milestone. Here's the template:

#### 4.1 Create Your Setup Documentation

```bash
cat > ~/sentinel-claudemem-eval/SETUP.md << 'EOF'
# claude-mem + Claude Code CLI: Setup for Sentinel Hub GIS Practitioners

## What This Solves
[Your summary of the stateless memory problem in your workflow]

## Installation
```bash
npm install -g claude-mem
claude-mem init
```

## Configuration for Sentinel Hub Work
[Paste your working config.json]

## Memory Seeding Template for GIS Projects
[Paste your memory.md template]

## Measured Results
- Baseline correction ratio: [X]%
- Post-claude-mem correction ratio: [X]%
- Reduction achieved: [X]%

## Workflow Integration
[Your step-by-step for starting sessions]

## Limitations and Gotchas
[What didn't work well; edge cases]
EOF
```

#### 4.2 Capture Your `memory.md` as a Shareable Template

```bash
# Sanitize and export (remove any credentials or sensitive paths)
claude-mem export --sanitize > sentinel-hub-memory-template.md
```

---

## 4. Validation

### How to Verify You Completed the Exercise Successfully

Work through this checklist:

#### Installation Validation
```bash
# 1. claude-mem is installed and functional
claude-mem --version
# Expected: version number printed (e.g., 1.x.x)

# 2. Project is initialized
ls -la ~/sentinel-claudemem-eval/.claude-mem/
# Expected: config.json, sessions/, memory.md

# 3. Memory file is populated
wc -l ~/sentinel-claudemem-eval/.claude-mem/memory.md
# Expected: >20 lines after seeding

# 4. Memory injection works
cd ~/sentinel-claudemem-eval && claude-mem inject
# Expected: Formatted context block printed to stdout
```

#### Session Validation
```bash
# 5. Session logs exist for all three sessions
ls ~/sentinel-claudemem-eval/.claude-mem/sessions/
# Expected: 3+ session log files

# 6. Memory grew across sessions (compression working)
# Compare timestamps and content of memory.md
git log --oneline .claude-mem/memory.md  # If using git
# OR
# Check that "Session History" section has entries for sessions 2 and 3
grep "Session" ~/sentinel-claudemem-eval/.claude-mem/memory.md
```

#### Outcome Validation
```bash
# 7. Tally sheet is complete
cat ~/sentinel-claudemem-eval/tally.md
# Expected: All three sessions with prompt counts filled in

# 8. Reduction calculated
# You should be able to state: "My correction ratio dropped from X% to Y%"
```

#### Content Validation

Open each of the three scripts you produced:
- [ ] **Session 1:** Single-image True Color fetch with cloud masking — works end-to-end
- [ ] **Session 2:** Multi-temporal fetch producing dated GeoTIFFs — works end-to-end
- [ ] **Session 3:** Refactored `SentinelProcessor` class with `argparse` CLI — importable and runnable

Run a quick smoke test:

```bash
# Test your Session 3 output
python sentinel_processor.py --help
# Expected: argparse help output with your defined arguments

python sentinel_processor.py \
  --mode single \
  --bbox "12.0,41.0,13.0,42.0" \
  --date "2024-06-01" \
  --output ./test_output/
# Expected: GeoTIFF written to test_output/
```

---

## 5. Next Steps

### Immediate Improvements

**1. Automate memory injection via a shell alias**

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias claude-sh='cd ~/sentinel-claudemem-eval && claude-mem start -- claude'

# Now starting a Sentinel Hub session is just:
claude-sh
```

**2. Version-control your memory**

```bash
cd ~/sentinel-claudemem-eval
git init
echo "sessions/" >> .gitignore  # Raw logs can be noisy
git add .claude-mem/memory.md .claude-mem/config.json
git commit -m "Initial claude-mem setup for Sentinel Hub scripting"
```

This lets you track how your memory evolves and roll back if compression degrades important context.

**3. Create domain-specific memory templates**

Consider separate memory files for different GIS workflows:

```
.claude-mem/
├── memory-sentinel2.md      # S2-specific conventions
├── memory-sar.md            # SAR/S1 conventions  
├── memory-byoc.md           # Custom collections
└── memory.md                # Active (symlink to current)
```

### Expanding the Evaluation

**4. Test with more complex tasks**

The 30% threshold is a starting bar. Push further with:
- Multi-sensor fusion scripts (S1 + S2)
- Statistical time-series analysis with `xarray`
- Batch processing pipelines with error recovery

**5. Evaluate memory compression quality**

```bash
# After 10+ sessions, audit what was kept vs. dropped
claude-mem audit

# Ask Claude directly:
# "Based on the injected memory, what do you know about 
#  my Sentinel Hub project's conventions?"
```

### Publishing Your Results

**6. Write the Tool Critic Post**

If you hit ≥30%, your evaluation is worth publishing. Structure it as:

1. **The problem** (stateless Claude sessions in GIS workflows)
2. **The experiment** (3-session controlled evaluation)
3. **The results** (your numbers, with honest caveats)
4. **The setup** (reproducible steps from your `SETUP.md`)
5. **Who should use this** (iterative EvalScript development, long-running GIS projects)

**7. Contribute back to `claude-mem`**

Your GIS-specific memory template is genuinely useful to others. Consider:
- Opening a PR to add a `sentinel-hub` example template to the repo
- Filing an issue if you found edge cases in memory compression
- Starring the repo and sharing in GIS/remote sensing communities

### Further Learning

| Resource | Why It's Relevant |
|---|---|
| [Sentinel Hub Process API docs](https://docs.sentinel-hub.com/api/latest/api/process/) | Master the API you're automating |
| [sentinelhub-py documentation](https://sentinelhub-py.readthedocs.io/) | Library reference for your scripts |
| [Claude Code CLI documentation](https://docs.anthropic.com/en/docs/claude-code) | Get more from the CLI you're augmenting |
| [claude-mem GitHub Issues](https://github.com/thedotmack/claude-mem/issues) | See known limitations, contribute findings |
| [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) | Patterns for agent memory and context management |

---

## Appendix: Quick Reference Card

```
# Daily Workflow with claude-mem

# Start a session
cd ~/sentinel-claudemem-eval
claude-mem start -- claude

# During the session
# → Work normally in Claude Code CLI
# → Tally correction prompts in tally.md

# End the session
# → Exit Claude Code (Ctrl+D or 'exit')
# → claude-mem auto-saves and compresses

# Check what was remembered
cat .claude-mem/memory.md

# Manually add a critical convention
claude-mem note "Always use EPSG:32633 for local raster processing"

# See session history
claude-mem list

# Export sanitized setup for sharing
claude-mem export --sanitize > my-gis-setup.md
```

---

*Exercise estimated time: 3–5 hours across multiple days (one session per day recommended for realistic memory accumulation)*

*Curriculum version: 1.0 | Designed for claude-mem + Claude Code CLI + Sentinel Hub API*