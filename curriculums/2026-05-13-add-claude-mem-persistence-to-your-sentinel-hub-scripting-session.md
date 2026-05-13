# Add `claude-mem` Persistence to Your Sentinel Hub Scripting Session

## A Hands-On Tutorial for Stateful GIS Automation with Claude Code

---

## 1. Introduction & Context

### The Problem: Claude Code Forgets Everything

When you're building multi-step GIS automation pipelines — querying Sentinel Hub APIs, iterating on band combinations, refining cloud-masking scripts — you constantly re-explain context to Claude. Every new session starts cold:

> *"I'm working with Sentinel-2 L2A data, my AOI is the Mekong Delta, I'm using NDVI + SWIR for flood mapping, my auth token is stored in `.env`, and last time we got the temporal compositing wrong..."*

This repeated "context tax" is a real overhead, especially across multi-day workflows.

### The Solution: `claude-mem`

[`claude-mem`](https://github.com/thedotmack/claude-mem) is a lightweight persistent memory layer for Claude Code agents. It:

- **Captures** session activity (your prompts, Claude's responses, code produced)
- **Compresses** that history using AI summarization
- **Injects** relevant context automatically into future sessions

Think of it as a project notebook that briefs Claude at the start of each session, so you never re-explain your Sentinel Hub setup again.

### Why This Matters for Sentinel Hub Workflows

Sentinel Hub scripting is inherently stateful:
- Evalscript development is iterative (you tweak, test, tweak again)
- AOIs, date ranges, and layer configurations persist across analysis steps
- Debugging often requires knowing *what you tried before*

With `claude-mem`, Claude remembers your evalscripts, your API configuration patterns, and your analytical decisions — session to session.

---

## 2. Prerequisites

Before starting, ensure you have the following:

### Required

| Requirement | Version | Check Command |
|---|---|---|
| Node.js | ≥ 18.x | `node --version` |
| npm | ≥ 9.x | `npm --version` |
| Claude Code CLI | Latest | `claude --version` |
| A Claude API key | — | Set as `ANTHROPIC_API_KEY` |
| Git | Any recent | `git --version` |

### Recommended Knowledge

- Basic familiarity with Claude Code (`claude` CLI)
- Some experience with Sentinel Hub Process API or evalscripts
- Comfortable running commands in a terminal

### Sentinel Hub Setup (Lightweight)

You don't need a full Sentinel Hub subscription to complete this tutorial. We'll use a **mock workflow** that mirrors real Sentinel Hub API patterns. If you do have a Sentinel Hub account, you can substitute real API calls at the marked steps.

### Environment Setup Check

Run this before proceeding:

```bash
# Verify Node.js
node --version   # Should print v18.x or higher

# Verify Claude Code is installed and authenticated
claude --version
claude whoami    # Should show your account

# Verify API key is set
echo $ANTHROPIC_API_KEY | head -c 10  # Should print first 10 chars
```

---

## 3. Step-by-Step Guide

### Phase 1: Install and Configure `claude-mem`

#### Step 1.1 — Clone and Install `claude-mem`

```bash
# Clone the repository
git clone https://github.com/thedotmack/claude-mem.git
cd claude-mem

# Install dependencies
npm install

# Build the project (if a build step exists)
npm run build 2>/dev/null || echo "No build step required"

# Link globally so it's available anywhere on your system
npm link
```

Verify the installation:

```bash
claude-mem --version
# or
claude-mem --help
```

You should see the `claude-mem` CLI help output. If `npm link` didn't work, try:

```bash
npm install -g .
```

#### Step 1.2 — Initialize a Project Memory Store

Create your Sentinel Hub project workspace:

```bash
# Create your working directory
mkdir -p ~/projects/sentinel-hub-analysis
cd ~/projects/sentinel-hub-analysis

# Initialize claude-mem for this project
claude-mem init
```

This creates a `.claude-mem/` directory in your project folder. Inspect it:

```bash
ls -la .claude-mem/
# Expected output:
# .claude-mem/
#   config.json      ← memory store configuration
#   sessions/        ← raw session capture storage
#   summaries/       ← AI-compressed context summaries
```

#### Step 1.3 — Configure `claude-mem`

Open the generated config file:

```bash
cat .claude-mem/config.json
```

Edit it to match your project context:

```json
{
  "project": "sentinel-hub-analysis",
  "description": "Sentinel Hub API workflow for flood mapping and vegetation analysis",
  "memoryDepth": 5,
  "autoInject": true,
  "compressionModel": "claude-3-haiku-20240307",
  "contextTags": ["evalscript", "sentinel-hub", "AOI", "band-combination", "NDVI"]
}
```

> **Note:** `memoryDepth: 5` means the last 5 compressed sessions will be injected as context. Adjust based on your project complexity.

---

### Phase 2: Set Up Your Sentinel Hub Scripting Environment

#### Step 2.1 — Create Project Structure

```bash
cd ~/projects/sentinel-hub-analysis

# Create the project layout
mkdir -p {evalscripts,outputs,config,scripts}

# Create a mock Sentinel Hub config (replace with real values if you have them)
cat > config/sentinelhub.env << 'EOF'
# Sentinel Hub Configuration
SH_CLIENT_ID=your_client_id_here
SH_CLIENT_SECRET=your_client_secret_here
SH_INSTANCE_ID=your_instance_id_here
SH_BASE_URL=https://services.sentinel-hub.com

# Area of Interest: Mekong Delta (example)
AOI_BBOX="102.0,9.5,107.5,12.5"
AOI_CRS="EPSG:4326"

# Analysis Date Range
DATE_FROM="2024-01-01"
DATE_TO="2024-03-31"
EOF
```

#### Step 2.2 — Create a Baseline Evalscript

This is the kind of file Claude will help you write and iterate on:

```bash
cat > evalscripts/ndvi_flood_baseline.js << 'EOF'
//VERSION=3
// Sentinel-2 NDVI + SWIR Flood Detection Evalscript
// Session 1 baseline - Mekong Delta flood mapping
// Created: Initial setup

function setup() {
  return {
    input: [{
      bands: ["B04", "B08", "B11", "B12", "SCL"],
      units: "DN"
    }],
    output: {
      bands: 4,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // Cloud masking using Scene Classification Layer
  if ([3, 8, 9, 10, 11].includes(sample.SCL)) {
    return [NaN, NaN, NaN, NaN];
  }

  // NDVI: (NIR - Red) / (NIR + Red)
  const ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);

  // NDWI (Modified): (Green - SWIR) proxy using B08 and B11
  const ndwi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);

  // Simple flood probability: low NDVI + high NDWI
  const floodProbability = (ndwi > 0.2 && ndvi < 0.3) ? 1.0 : 0.0;

  return [ndvi, ndwi, floodProbability, 1.0]; // [NDVI, NDWI, Flood, Valid]
}
EOF
```

#### Step 2.3 — Create a Mock API Query Script

```bash
cat > scripts/query_sentinel.py << 'EOF'
#!/usr/bin/env python3
"""
Mock Sentinel Hub Process API query script.
Replace mock responses with real sentinelhub-py calls if you have credentials.
"""

import json
import os
from datetime import datetime

# Load config
AOI_BBOX = os.getenv("AOI_BBOX", "102.0,9.5,107.5,12.5").split(",")
DATE_FROM = os.getenv("DATE_FROM", "2024-01-01")
DATE_TO = os.getenv("DATE_TO", "2024-03-31")

def build_process_request(evalscript_path: str) -> dict:
    """Build a Sentinel Hub Process API request payload."""
    with open(evalscript_path) as f:
        evalscript = f.read()

    return {
        "input": {
            "bounds": {
                "bbox": [float(x) for x in AOI_BBOX],
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{DATE_FROM}T00:00:00Z",
                        "to": f"{DATE_TO}T23:59:59Z"
                    },
                    "maxCloudCoverage": 20
                }
            }]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]
        },
        "evalscript": evalscript
    }

def mock_execute_query(request: dict) -> dict:
    """Simulates a Sentinel Hub API response for tutorial purposes."""
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "tiles_found": 14,
        "cloud_free_tiles": 9,
        "output_path": "outputs/ndvi_flood_result.tif",
        "stats": {
            "mean_ndvi": 0.42,
            "mean_ndwi": 0.18,
            "flood_coverage_pct": 12.3
        }
    }

if __name__ == "__main__":
    print("Building Sentinel Hub Process API request...")
    request = build_process_request("evalscripts/ndvi_flood_baseline.js")
    print(f"Request built for AOI: {AOI_BBOX}")
    print(f"Date range: {DATE_FROM} → {DATE_TO}")

    print("\nExecuting query (mock)...")
    result = mock_execute_query(request)

    print("\n=== Query Results ===")
    print(json.dumps(result, indent=2))

    # Save results log
    with open("outputs/session1_results.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nResults saved to outputs/session1_results.json")
EOF

# Make it executable
chmod +x scripts/query_sentinel.py
mkdir -p outputs
```

---

### Phase 3: Run Session 1 — Initial Analysis with Memory Capture

#### Step 3.1 — Start a `claude-mem`-Wrapped Claude Session

The key pattern is wrapping your `claude` invocations with `claude-mem`:

```bash
cd ~/projects/sentinel-hub-analysis

# Start a memory-tracked Claude Code session
claude-mem session start --tag "session1-ndvi-baseline"
```

> **Alternative invocation** (if `claude-mem` patches the Claude CLI directly):
> ```bash
> claude-mem run claude
> ```
> Check `claude-mem --help` for the exact invocation pattern in the version you installed.

#### Step 3.2 — Work Through Your Analysis in Session 1

Inside your Claude Code session, run through this multi-step workflow. Type each prompt naturally — `claude-mem` is capturing everything in the background:

**Prompt 1: Establish project context**
```
I'm working on a Sentinel Hub flood mapping pipeline for the Mekong Delta.
I'm using Sentinel-2 L2A data with an evalscript that computes NDVI and NDWI
for flood detection. My config is in config/sentinelhub.env and my baseline
evalscript is at evalscripts/ndvi_flood_baseline.js.

Please read both files and summarize the current approach.
```

**Prompt 2: Run and analyze**
```
Run the query script at scripts/query_sentinel.py and analyze the output.
The mock results will simulate real Sentinel Hub API responses.
What do the statistics tell us about flood coverage in this period?
```

**Prompt 3: Identify improvements**
```
The flood coverage is 12.3% but I suspect the NDWI threshold of 0.2 is too
conservative. Can you suggest a refined threshold and update the evalscript?
Also, I want to add a temporal compositing function to reduce noise.
```

**Prompt 4: Document decisions**
```
Please update the evalscript comment header with:
1. Today's date
2. The threshold change we made (NDWI 0.2 → 0.15)
3. The reasoning: higher sensitivity needed for shallow inundation detection
4. Next session TODO: add temporal compositing, test on dry season data
```

#### Step 3.3 — End Session 1 and Compress Memory

```bash
# End the session — this triggers AI compression of the session log
claude-mem session end --summarize
```

You should see output like:

```
✓ Session captured: 4 interactions, ~2,400 tokens
✓ Compressing session with AI...
✓ Summary saved to .claude-mem/summaries/session1-ndvi-baseline.md
✓ Memory store updated (5 sessions tracked)
```

Inspect what was captured:

```bash
cat .claude-mem/summaries/session1-ndvi-baseline.md
```

You should see a structured summary like:

```markdown
## Session Summary: session1-ndvi-baseline
**Date:** 2024-XX-XX
**Project:** Sentinel Hub flood mapping, Mekong Delta

### Key Decisions Made:
- NDWI threshold lowered from 0.2 → 0.15 for shallow inundation sensitivity
- Evalscript updated with new threshold
- Cloud masking using SCL band confirmed working

### Files Modified:
- `evalscripts/ndvi_flood_baseline.js` (threshold update + header docs)

### Outstanding TODOs:
- Add temporal compositing function
- Test evalscript on dry season date range (June–August 2024)
- Validate flood coverage % against known inundation records

### Technical Context:
- AOI: Mekong Delta (bbox: 102.0,9.5,107.5,12.5)
- Data: Sentinel-2 L2A, max 20% cloud cover
- Mock query returned: 14 tiles, 9 cloud-free, 12.3% flood coverage
```

---

### Phase 4: Run Session 2 — Continue with Context Injection

This is the payoff. Start a fresh terminal session (simulating a new day):

#### Step 4.1 — Simulate a Fresh Session Start

```bash
# Open a new terminal, or clear your shell history to simulate freshness
cd ~/projects/sentinel-hub-analysis

# Start Session 2 — claude-mem will auto-inject previous context
claude-mem session start --tag "session2-temporal-compositing"
```

Watch the console output:

```
📚 Loading memory context...
✓ Found 1 previous session summary
✓ Injecting context from: session1-ndvi-baseline
✓ Context token budget used: ~380 tokens
🚀 Starting Claude Code session with memory context...
```

#### Step 4.2 — Verify Context Was Injected

Start your session with a test prompt — **do not re-explain your project**:

```
What were we working on last session, and what did we decide to do next?
```

**Expected response** (Claude should answer without you providing any background):

> *"Last session we were working on a Sentinel Hub flood mapping pipeline for the Mekong Delta using Sentinel-2 L2A data. The key decision was lowering the NDWI threshold from 0.2 to 0.15 for better shallow inundation detection. The outstanding TODOs were: (1) add temporal compositing to reduce noise, (2) test on dry season data from June–August 2024, and (3) validate results against known inundation records. Want to start with the temporal compositing function?"*

If Claude answers this accurately **without you re-explaining**, memory injection is working. ✓

#### Step 4.3 — Continue the Workflow (Picking Up Where You Left Off)

```
Yes, let's implement the temporal compositing function. It should:
- Accept a time window of N images
- Use median compositing to reduce cloud/shadow noise
- Output a single cloud-free composite NDVI/NDWI image
Add it to the existing evalscript.
```

```
Now update the query script to use a dry season date range
(2024-06-01 to 2024-08-31) and run it. Compare the flood coverage
percentage to the wet season results from last session.
```

```
Write a summary comparison of wet season vs dry season results
and save it to outputs/seasonal_comparison.md
```

#### Step 4.4 — End Session 2

```bash
claude-mem session end --summarize
```

---

### Phase 5: Measure the Overhead Reduction

#### Step 5.1 — Count Your Context-Setting Prompts

Create a measurement log:

```bash
cat > outputs/memory_effectiveness_log.md << 'EOF'
# Claude-mem Effectiveness Measurement

## Session 1 (Without Prior Memory)
- Context-setting prompts required: 1 (full project explanation)
- Tokens spent on context: ~180 tokens
- Prompts before productive work began: 2

## Session 2 (With Memory Injection)
- Context-setting prompts required: 0
- Tokens spent on context: 0 (injected automatically, ~380 tokens)
- Prompts before productive work began: 1 (immediate continuation)

## Observations
- [ ] Claude correctly recalled NDWI threshold change (0.2 → 0.15)
- [ ] Claude recalled AOI and data source without prompting
- [ ] Claude recalled outstanding TODOs
- [ ] Session 2 reached productive work 1 prompt faster

## Qualitative Assessment
Repeated context overhead: HIGH / MEDIUM / LOW (circle one)
Memory injection accuracy: HIGH / MEDIUM / LOW (circle one)
EOF
```

Fill this in after completing both sessions. The key metric: **did you have to re-explain your Sentinel Hub setup in Session 2?**

#### Step 5.2 — View the Full Memory Store

```bash
# List all captured sessions
claude-mem list

# View the combined memory context that would be injected
claude-mem context show

# Check token usage
claude-mem stats
```

---

## 4. Validation

Run through this checklist to confirm you've completed the exercise successfully:

### ✅ Installation Validation

```bash
# 1. claude-mem is installed and accessible
claude-mem --version
# Expected: prints a version string

# 2. Memory store was initialized
ls .claude-mem/
# Expected: config.json, sessions/, summaries/ directories exist

# 3. Session 1 summary was created
ls .claude-mem/summaries/
# Expected: session1-ndvi-baseline.md exists
```

### ✅ Memory Capture Validation

```bash
# Session summary contains key decisions
grep -i "NDWI" .claude-mem/summaries/session1-ndvi-baseline.md
# Expected: line mentioning threshold change 0.2 → 0.15

grep -i "temporal" .claude-mem/summaries/session1-ndvi-baseline.md
# Expected: reference to temporal compositing TODO
```

### ✅ Context Injection Validation

Open `.claude-mem/summaries/session1-ndvi-baseline.md` and confirm it contains:

- [ ] The AOI (Mekong Delta / bbox coordinates)
- [ ] The threshold decision (NDWI 0.2 → 0.15)
- [ ] At least one TODO item for the next session
- [ ] References to the evalscript file that was modified

### ✅ Cross-Session Continuity Validation

In Session 2, Claude should have:

- [ ] Recalled the project without you re-explaining it
- [ ] Known the NDWI threshold that was changed
- [ ] Referenced the outstanding TODOs from Session 1
- [ ] Picked up work at the "temporal compositing" step

### ✅ File Output Validation

```bash
# Check all expected outputs exist
ls -la outputs/
# Expected files:
# session1_results.json
# seasonal_comparison.md
# memory_effectiveness_log.md

# Check evalscript was updated
grep "0.15" evalscripts/ndvi_flood_baseline.js
# Expected: NDWI threshold 0.15 appears in the script
```

### ✅ Overhead Reduction Assessment

Look at your `memory_effectiveness_log.md`. A successful outcome shows:
- **Session 2 required 0 context-setting prompts** (vs 1–2 in Session 1)
- **Claude correctly recalled at least 3 specific facts** from Session 1 without prompting

---

## 5. Next Steps

You've successfully added persistent memory to your Claude Code + Sentinel Hub workflow. Here's where to go next:

### Immediate Enhancements

**5.1 — Add Custom Memory Tags**

Tag your sessions with domain-specific keywords for better retrieval:

```bash
claude-mem session start --tag "session3-validation" --context-tags "flood,validation,accuracy-assessment"
```

**5.2 — Create a Project Memory Template**

Pre-seed memory with your standing project context so every session starts informed:

```bash
cat > .claude-mem/project-context.md << 'EOF'
# Sentinel Hub Analysis Project — Standing Context

## Project Overview
Flood mapping pipeline for the Mekong Delta using Sentinel-2 L2A.

## Tech Stack
- Sentinel Hub Process API
- Python + sentinelhub-py
- Custom evalscripts (JavaScript)
- Claude Code for script generation and iteration

## Key Configuration
- AOI: Mekong Delta (EPSG:4326 bbox: 102.0,9.5,107.5,12.5)
- Cloud threshold: 20% max
- Primary indices: NDVI, NDWI, flood probability layer

## Known Issues / Watch-outs
- SCL-based cloud masking misses thin cirrus (SCL class 10)
- SWIR band (B11) has occasional striping in some tiles

## Useful File Paths
- Evalscripts: ./evalscripts/
- Config: ./config/sentinelhub.env
- Results: ./outputs/
EOF

claude-mem context seed --file .claude-mem/project-context.md
```

**5.3 — Multi-Project Memory Isolation**

If you work on multiple GIS projects, initialize separate memory stores:

```bash
# Each project gets its own isolated memory
cd ~/projects/landcover-classification && claude-mem init
cd ~/projects/sentinel-hub-analysis && claude-mem init
```

### Expand Your Workflow

**5.4 — Automate Session Wrapping**

Add a shell alias so you never forget to wrap Claude with memory:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias claude-gis='claude-mem session start && claude && claude-mem session end --summarize'
```

**5.5 — Integrate with Real Sentinel Hub API**

Replace the mock script with real `sentinelhub-py` calls:

```bash
pip install sentinelhub
```

```python
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, BBox, CRS, MimeType

config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

# Now claude-mem will remember your real API patterns session-to-session
```

**5.6 — Export Memory as Project Documentation**

```bash
# Generate a human-readable project history from memory
claude-mem export --format markdown --output docs/analysis-history.md

# This doubles as project documentation for collaborators
```

### Further Learning

| Topic | Resource |
|---|---|
| `claude-mem` advanced configuration | [GitHub README](https://github.com/thedotmack/claude-mem) |
| Sentinel Hub evalscript docs | [Sentinel Hub Documentation](https://docs.sentinel-hub.com/api/latest/evalscript/) |
| Claude Code CLI patterns | [Anthropic Docs](https://docs.anthropic.com) |
| GIS automation with Python | `sentinelhub-py` library docs |

### Reflect on Your Workflow

After completing this tutorial, ask yourself:

1. **How many sessions in my typical workflow involve re-explaining the same context?** Each of those is an `claude-mem` win waiting to happen.

2. **What's my "standing context" that never changes?** Seed it into `project-context.md` once and never repeat it.

3. **Are there decisions I keep revisiting?** Memory compression means those decisions are documented automatically — no more "why did we choose that threshold again?"

---

> **💡 Pro Tip:** The real power of `claude-mem` compounds over time. After 10+ sessions on a project, Claude will have a rich, compressed history of every technical decision you've made — essentially becoming a domain expert on *your specific project* rather than starting fresh every time.

---

*Tutorial complete. You've added stateful memory to your Claude Code GIS workflow.*