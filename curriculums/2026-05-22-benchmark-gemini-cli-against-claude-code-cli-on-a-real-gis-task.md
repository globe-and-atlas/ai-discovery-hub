# Benchmark Gemini CLI Against Claude Code CLI on a Real GIS Task

## A Tool Critic's Field Guide for GIS/AI Practitioners

---

## 1. Introduction & Context

Google's **Gemini CLI** is an open-source, Apache 2.0-licensed terminal AI agent that drops Gemini directly into your shell — no browser, no IDE extension required. It's a direct structural competitor to Anthropic's Claude Code CLI, and its free tier (60 requests/min, 1,000 requests/day with a personal Google account) makes the barrier to a genuine benchmark effectively zero.

Why should you run this test yourself? Because every existing Gemini CLI review was written by a general developer. Their benchmarks cover "write a React component" or "explain this Python stack trace." None of them will hand both tools the same **FME workspace generation task** or **Sentinel Hub API scripting problem** and compare:

- Output correctness in a domain with real spatial semantics
- Token transparency and context window utilization (Gemini's 1M-token window is a genuine differentiator)
- Tool-use patterns — does the agent read your local `.fmw` files? Does it shell out to GDAL?
- Wall-clock speed under equivalent prompts

By writing this up as a **Tool Critic piece**, you produce content that general developer reviewers cannot replicate. Your GIS-specific test case is your differentiated signal.

**What you'll build in this tutorial:**

1. A reproducible benchmark harness: two identical GIS prompts, two CLIs, structured output capture
2. A scoring rubric tailored to spatial domain correctness
3. A publishable comparison write-up template

---

## 2. Prerequisites

### Software

| Requirement | Minimum Version | Check Command |
|---|---|---|
| Node.js | v18+ (LTS recommended) | `node --version` |
| npm | v9+ | `npm --version` |
| Claude Code CLI | Latest | `claude --version` |
| Git | Any recent | `git --version` |
| Python | 3.9+ (for result parsing) | `python3 --version` |

### Accounts & Credentials

- **Google Account** — for Gemini CLI OAuth (free tier, no credit card)
- **Anthropic account** — Claude Code CLI already authenticated (assumed from your existing workflow)
- Optional: `GOOGLE_CLOUD_PROJECT` env var if you have a paid Code Assist license

### GIS-Specific Assets

Prepare **at least one** of the following before starting:

```
your-benchmark-workspace/
├── sample.fmw              # An existing FME workspace (even a simple one)
├── sentinel_area.geojson   # A small AOI polygon for Sentinel Hub queries
├── sample_data.gpkg        # Optional: a GeoPackage for transformation tasks
└── GEMINI.md               # We will create this — project context file
```

> **If you don't have an `.fmw` file handy:** A one-transformer FME workspace reading a Shapefile and writing to GeoJSON is sufficient. Alternatively, use the Sentinel Hub scripting task exclusively — it requires only the `.geojson` AOI file.

### Install `jq` and `tee` (for output capture)

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

---

## 3. Step-by-Step Guide

---

### Phase 0 — Set Up Your Benchmark Directory

Create a clean, isolated working directory. **Both CLIs will be run from here** so their file-reading tools see identical context.

```bash
mkdir gis-cli-benchmark && cd gis-cli-benchmark

# Copy in your GIS assets
cp /path/to/your/sample.fmw .
cp /path/to/your/sentinel_area.geojson .

# Create a timestamped results directory
mkdir -p results/gemini results/claude
```

---

### Phase 1 — Install Gemini CLI

The source material provides three installation paths. Choose the one that fits your environment:

#### Option A: Global npm install (recommended for benchmarking — stable, inspectable)

```bash
npm install -g @google/gemini-cli@latest
```

Verify:

```bash
gemini --version
```

#### Option B: npx (no install, always latest — good for a one-off test)

```bash
npx @google/gemini-cli
```

> **Note on release channels:** The source defines `latest` (stable, promoted weekly Tuesday 20:00 UTC), `preview` (weekly Tuesday 23:59 UTC, less vetted), and `nightly` (daily, main branch). For a publishable benchmark, **use `@latest`** so your results are reproducible by readers. State this explicitly in your write-up.

#### Option C: Homebrew (macOS/Linux)

```bash
brew install gemini-cli
```

---

### Phase 2 — Authenticate Gemini CLI

```bash
gemini
```

On first launch, Gemini CLI will prompt you to choose an authentication method. Select **"Sign in with Google"** and complete the browser OAuth flow.

Once authenticated, you'll land in the interactive REPL. Type `/quit` or `Ctrl+C` to exit — we'll re-enter with structured prompts in Phase 4.

> **If you have an organizational Code Assist license**, set your project first:
> ```bash
> export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
> gemini
> ```

> **Free tier limits to note in your write-up:** 60 requests/min, 1,000 requests/day. For a benchmark session, you will not hit these limits.

---

### Phase 3 — Create Your Project Context File (`GEMINI.md`)

Gemini CLI supports a `GEMINI.md` file in the project root for custom context injection — analogous to Claude's `CLAUDE.md`. This is a critical benchmark variable: **if you give Gemini your project context, do the same for Claude.**

```bash
cat > GEMINI.md << 'EOF'
# GIS Benchmark Project Context

## Environment
- FME Desktop 2024.x installed, `fme` available on PATH
- Python 3.11 with `sentinelhub`, `geopandas`, `shapely` installed
- GDAL 3.8 available via `ogrinfo`, `ogr2ogr`

## Data Assets in This Directory
- `sample.fmw` — FME workspace: reads a Shapefile, reprojects to EPSG:4326, writes GeoJSON
- `sentinel_area.geojson` — AOI polygon in EPSG:4326 for Sentinel-2 queries

## Conventions
- FME workspaces should use Published Parameters for input/output paths
- Sentinel Hub scripts should use the `sentinelhub` Python library (>=3.9)
- All output CRS: EPSG:4326 unless otherwise specified
- Error handling: always include try/except with meaningful spatial context in messages

## Do Not
- Invent file paths that don't exist in this directory
- Use deprecated FME transformers (check FME 2024 transformer list)
EOF
```

> **For Claude Code CLI**, create an equivalent `CLAUDE.md` with identical content, or symlink it:
> ```bash
> cp GEMINI.md CLAUDE.md
> ```

---

### Phase 4 — Define Your Two Benchmark Prompts

This is the heart of the exercise. You need prompts that are:

1. **Identical in specification** — both tools get the exact same text
2. **Spatially specific** — not solvable by a general developer without GIS knowledge
3. **Verifiable** — output can be checked for correctness

#### Prompt A: FME Workspace Generation Task

```
BENCHMARK_PROMPT_FME="You are an FME workspace developer. 
Examine the file sample.fmw in this directory to understand the existing pattern.
Then create a NEW FME workspace called reproject_and_clip.fmw that:
1. Reads features from an input GeoPackage (Published Parameter: INPUT_GPKG)
2. Reprojects features from their source CRS to EPSG:3857 (Web Mercator)
3. Clips features to the bounding box defined in sentinel_area.geojson
4. Writes the result to an output GeoPackage (Published Parameter: OUTPUT_GPKG)
5. Adds a Published Parameter called LOG_LEVEL with default value MEDIUM

Use FMEObjects XML format. Include a FeatureReader, Reprojector, Clipper, 
and FeatureWriter transformer. Add inline comments explaining each transformer's 
role. Verify your transformer names are valid in FME 2024."
```

#### Prompt B: Sentinel Hub API Scripting Task

```
BENCHMARK_PROMPT_SENTINEL="Read the file sentinel_area.geojson in this directory.
Write a complete, runnable Python script that:
1. Loads the AOI from sentinel_area.geojson using geopandas
2. Queries Sentinel Hub for Sentinel-2 L2A imagery over that AOI
3. Filters for scenes with cloud cover < 20% in the last 90 days
4. Downloads the least-cloudy scene as a GeoTIFF at 10m resolution
5. Computes NDVI from bands B04 and B08
6. Saves the NDVI raster as ndvi_output.tif in the current directory
7. Prints a summary: scene date, cloud cover %, NDVI min/max/mean

Use the sentinelhub Python library. Include a SHConfig() setup block at the 
top with placeholders for credentials. Handle the case where no scenes meet 
the cloud cover threshold. Include docstrings."
```

Save both prompts to files for reproducible execution:

```bash
cat > prompts/prompt_fme.txt << 'EOF'
[paste BENCHMARK_PROMPT_FME content here]
EOF

cat > prompts/prompt_sentinel.txt << 'EOF'
[paste BENCHMARK_PROMPT_SENTINEL content here]
EOF
```

```bash
mkdir -p prompts
```

---

### Phase 5 — Run Gemini CLI on Both Prompts

#### 5.1 — Run Prompt A (FME) with Gemini CLI

Capture the full session output including timing:

```bash
cd gis-cli-benchmark

# Start timer and run — pipe the prompt in non-interactively
time gemini < prompts/prompt_fme.txt 2>&1 | tee results/gemini/fme_output.txt

# Record the wall-clock time manually or parse from `time` output
```

> **Non-interactive mode note:** The source material states Gemini CLI supports running non-interactively in scripts. Piping via stdin is the standard shell approach. If your version requires a flag for non-interactive mode, consult `gemini --help` — the source content does not specify a dedicated `--no-interactive` flag, so **do not assume one exists**. If stdin piping doesn't work, use the interactive REPL and manually paste the prompt, capturing with `script`:

```bash
# Fallback: use script(1) to capture an interactive session
script -q results/gemini/fme_session.txt
gemini
# [paste prompt, wait for response, then /quit]
exit
```

#### 5.2 — Run Prompt B (Sentinel Hub) with Gemini CLI

```bash
time gemini < prompts/prompt_sentinel.txt 2>&1 | tee results/gemini/sentinel_output.txt
```

#### 5.3 — Observe and Note During Each Run

While Gemini CLI responds, watch for and annotate in a scratchpad:

```bash
cat > results/gemini/observations.md << 'EOF'
# Gemini CLI Live Observations

## FME Task
- Did it read sample.fmw before generating? (tool-use: file read) Y/N
- Did it read sentinel_area.geojson? Y/N  
- Did it invoke any shell commands? Y/N — if yes, what?
- Did it use Google Search grounding? Y/N
- Approximate time to first token: __s
- Approximate time to complete response: __s
- Any visible token/context info displayed? Y/N

## Sentinel Hub Task
- Did it read sentinel_area.geojson? Y/N
- Did it attempt to verify library imports? Y/N
- Did it use Google Search grounding? Y/N
- Approximate time to first token: __s
- Approximate time to complete response: __s
EOF
```

---

### Phase 6 — Run Claude Code CLI on the Same Prompts

Assuming you have Claude Code CLI already configured in your workflow:

```bash
# Adjust the command to match your Claude Code CLI invocation pattern
# Common patterns — use whichever matches your setup:

# Pattern 1: stdin pipe
time claude < prompts/prompt_fme.txt 2>&1 | tee results/claude/fme_output.txt

time claude < prompts/prompt_sentinel.txt 2>&1 | tee results/claude/sentinel_output.txt

# Pattern 2: -p / --print flag (non-interactive, if supported by your version)
# time claude -p "$(cat prompts/prompt_fme.txt)" 2>&1 | tee results/claude/fme_output.txt
```

```bash
# Mirror the same observation template
cp results/gemini/observations.md results/claude/observations.md
# Fill in equivalent fields for Claude
```

> **Critical for fairness:** Run both CLIs from the **same directory** (`gis-cli-benchmark/`) so both have access to `sample.fmw`, `sentinel_area.geojson`, `GEMINI.md`/`CLAUDE.md`, and identical filesystem context.

---

### Phase 7 — Score Each Output

Create a scoring rubric. This is what makes your benchmark publishable — a GIS-specific rubric that general reviewers don't have.

#### 7.1 — Create the Rubric File

```bash
cat > results/scoring_rubric.md << 'EOF'
# GIS CLI Benchmark Scoring Rubric

Each criterion scored 0–3:
  0 = Not attempted / completely wrong
  1 = Attempted but significant errors
  2 = Mostly correct, minor issues
  3 = Correct and production-ready

## Task A: FME Workspace Generation

| Criterion | Max | Gemini | Claude |
|---|---|---|---|
| Used FeatureReader/FeatureWriter correctly | 3 | | |
| Reprojector targets EPSG:3857 (not hardcoded EPSG:4326) | 3 | | |
| Clipper uses sentinel_area.geojson bounding box (read from file, not hallucinated) | 3 | | |
| Published Parameters: INPUT_GPKG, OUTPUT_GPKG, LOG_LEVEL with defaults | 3 | | |
| Transformer names valid in FME 2024 (no deprecated transformers) | 3 | | |
| FMEObjects XML is syntactically parseable | 3 | | |
| Inline comments present | 3 | | |
| Read sample.fmw to infer pattern (tool use) | 3 | | |
| **TOTAL** | **24** | | |

## Task B: Sentinel Hub Scripting

| Criterion | Max | Gemini | Claude |
|---|---|---|---|
| Loads AOI from sentinel_area.geojson (uses the actual file) | 3 | | |
| Correct SHConfig() setup block with credential placeholders | 3 | | |
| DataCollection.SENTINEL2_L2A used (not L1C) | 3 | | |
| Cloud cover filter < 20% implemented correctly | 3 | | |
| 90-day date range calculated dynamically (not hardcoded dates) | 3 | | |
| 10m resolution specified correctly for Sentinel-2 | 3 | | |
| NDVI formula correct: (B08 - B04) / (B08 + B04) | 3 | | |
| ndvi_output.tif saved to current directory | 3 | | |
| Summary print: date, cloud%, NDVI min/max/mean | 3 | | |
| No-scenes-found edge case handled | 3 | | |
| Docstrings present | 3 | | |
| **TOTAL** | **33** | | |

## Behavioral Metrics (qualitative 0–3 each)

| Metric | Gemini | Claude |
|---|---|---|
| File reading (actually used local files before generating) | | |
| Token/context transparency (showed usage, model info) | | |
| Hallucination rate (invented APIs, paths, transformer names) | | |
| Response speed (subjective: 3=fast, 1=slow) | | |
| Error recovery (if it hit an error, did it self-correct?) | | |

EOF
```

#### 7.2 — Validate the FME Output Structurally

Check whether the generated `.fmw` XML is at least parseable:

```bash
# Extract any XML block from Gemini's output
grep -A 1000 '<?xml' results/gemini/fme_output.txt | head -200 > results/gemini/extracted.fmw

# Validate XML structure
python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('results/gemini/extracted.fmw')
    print('XML VALID - root tag:', tree.getroot().tag)
except ET.ParseError as e:
    print('XML INVALID:', e)
"

# Repeat for Claude
grep -A 1000 '<?xml' results/claude/fme_output.txt | head -200 > results/claude/extracted.fmw
python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('results/claude/extracted.fmw')
    print('XML VALID - root tag:', tree.getroot().tag)
except ET.ParseError as e:
    print('XML INVALID:', e)
"
```

#### 7.3 — Validate the Sentinel Hub Script Structurally

```bash
# Extract the Python block from each output
python3 << 'PYEOF'
import re

for tool in ['gemini', 'claude']:
    with open(f'results/{tool}/sentinel_output.txt') as f:
        content = f.read()
    
    # Find Python code blocks
    blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
    if blocks:
        # Take the largest block (most likely the complete script)
        main_block = max(blocks, key=len)
        with open(f'results/{tool}/extracted_sentinel.py', 'w') as out:
            out.write(main_block)
        print(f"{tool}: extracted {len(main_block)} chars of Python")
    else:
        print(f"{tool}: no Python code block found")
PYEOF

# Syntax check each extracted script
python3 -m py_compile results/gemini/extracted_sentinel.py && echo "Gemini: syntax OK" || echo "Gemini: syntax ERROR"
python3 -m py_compile results/claude/extracted_sentinel.py && echo "Claude: syntax OK" || echo "Claude: syntax ERROR"
```

#### 7.4 — Check for Key GIS-Correctness Markers

```bash
python3 << 'PYEOF'
import re

checks = {
    'sentinel': {
        'DataCollection.SENTINEL2_L2A': 'Uses L2A (not L1C)',
        'cloud_coverage_percentage': 'Cloud cover field name correct',
        '(B08 - B04)': 'NDVI numerator correct',
        '(B08 + B04)': 'NDVI denominator correct',
        'SHConfig': 'SHConfig auth block present',
        'BBox': 'BBox used for spatial filter',
        'timedelta': 'Dynamic date range (not hardcoded)',
        'ndvi_output.tif': 'Correct output filename',
    }
}

for tool in ['gemini', 'claude']:
    try:
        with open(f'results/{tool}/extracted_sentinel.py') as f:
            code = f.read()
        print(f"\n=== {tool.upper()} Sentinel Script Checks ===")
        for pattern, description in checks['sentinel'].items():
            found = pattern in code
            status = "✅" if found else "❌"
            print(f"  {status} {description} ('{pattern}')")
    except FileNotFoundError:
        print(f"\n{tool}: extracted_sentinel.py not found — run Step 7.3 first")
PYEOF
```

---

### Phase 8 — Write Your Tool Critic Piece

Use this structure as your publishing template. The GIS-specific evidence you've collected fills in what general reviewers can't provide.

```bash
cat > results/tool_critic_draft.md << 'DRAFT'
# Gemini CLI vs Claude Code CLI: A GIS Practitioner's Honest Benchmark

**Test date:** [DATE]  
**Gemini CLI version:** [run `gemini --version`]  
**Claude Code version:** [run `claude --version`]  
**Test environment:** [your OS, Node version]

---

## Why This Test Is Different

[2–3 sentences: you ran FME workspace generation and Sentinel Hub scripting — 
tasks that require spatial domain knowledge to evaluate. General reviewer 
benchmarks don't cover this.]

---

## Setup Notes

- Both tools ran from the same directory with identical project context files
- Gemini CLI authenticated via Google OAuth (free tier: 60 req/min)
- Model: Gemini [version shown at startup] | Claude [version]
- Release channel: `@latest` (stable)

---

## Task A: FME Workspace Generation

### The Prompt
[paste your FME prompt]

### What Gemini Did
**Tool use:** Did it read sample.fmw first? [Y/N + what you observed]  
**Output:** [1–2 sentences on quality]  
**Score:** [X]/24  
**Notable issues:** [e.g., "Used deprecated SpatialRelator transformer; 
hallucinated a 'GeoPackageWriter2024' transformer that doesn't exist"]

### What Claude Did
**Tool use:** [Y/N]  
**Output:** [1–2 sentences]  
**Score:** [X]/24  
**Notable issues:** [...]

### Winner: [GEMINI / CLAUDE / TIE]
[2–3 sentences of analysis]

---

## Task B: Sentinel Hub API Scripting

### The Prompt
[paste your Sentinel prompt]

### What Gemini Did
**Tool use:** Did it read sentinel_area.geojson? [Y/N]  
**Google Search grounding:** [Y/N — did it ground against sentinelhub docs?]  
**Score:** [X]/33  
**Notable issues:** [...]

### What Claude Did
**Score:** [X]/33  
**Notable issues:** [...]

### Winner: [GEMINI / CLAUDE / TIE]

---

## Behavioral Comparison

| Metric | Gemini CLI | Claude Code |
|---|---|---|
| Speed (time to complete response) | [Xs] | [Xs] |
| Token transparency | [what it showed] | [what it showed] |
| File reading (used local context) | Y/N | Y/N |
| Google Search grounding | [observed?] | N/A |
| Hallucination rate (GIS-specific) | [X instances] | [X instances] |
| Context window usage | 1M available | [Claude's limit] |

---

## The One Differentiator That Matters for GIS

[Your honest take: for large-codebase or large-dataset-description tasks, 
does Gemini's 1M context window actually change what's possible? Did it 
read more of your local files unprompted? Or did Claude's tool-use 
patterns feel more controlled and predictable?]

---

## Recommendation

**Use Gemini CLI when:** [specific scenarios from your test]  
**Stick with Claude Code when:** [specific scenarios]  
**Free tier makes Gemini CLI worth having as:** [parallel tool / fallback / 
primary for X tasks]

---

## Reproducibility

All prompts, raw outputs, and scoring sheets: [link to your repo or gist]

DRAFT

echo "Draft template created at results/tool_critic_draft.md"
```

---

## 4. Validation

### Did You Complete the Exercise? Check Each Item:

```bash
# Run this checklist script
python3 << 'PYEOF'
import os

checks = [
    ("results/gemini/fme_output.txt", "Gemini FME output captured"),
    ("results/gemini/sentinel_output.txt", "Gemini Sentinel output captured"),
    ("results/claude/fme_output.txt", "Claude FME output captured"),
    ("results/claude/sentinel_output.txt", "Claude Sentinel output captured"),
    ("results/gemini/extracted.fmw", "Gemini FMW XML extracted"),
    ("results/claude/extracted.fmw", "Claude FMW XML extracted"),
    ("results/gemini/extracted_sentinel.py", "Gemini Python script extracted"),
    ("results/claude/extracted_sentinel.py", "Claude Python script extracted"),
    ("results/scoring_rubric.md", "Scoring rubric exists"),
    ("results/tool_critic_draft.md", "Tool Critic draft created"),
    ("results/gemini/observations.md", "Live observations recorded"),
    ("results/claude/observations.md", "Live observations recorded"),
]

passed = 0
for path, description in checks:
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    non_empty = size > 100  # files should have real content
    status = "✅" if (exists and non_empty) else ("⚠️ empty" if exists else "❌ missing")
    print(f"  {status}  {description}")
    if exists and non_empty:
        passed += 1

print(f"\n{passed}/{len(checks)} checks passed")
if passed == len(checks):
    print("🎉 Benchmark complete — ready to write up!")
elif passed >= len(checks) * 0.75:
    print("⚠️  Almost there — fill in the missing pieces above")
else:
    print("🔴 Significant gaps — revisit Phases 5–7")
PYEOF
```

### Quality Gate: Your Write-Up Is Publishable When

- [ ] Both tools were scored on the **same rubric** with the **same prompts**
- [ ] You have at least **one concrete GIS-correctness finding** (e.g., wrong EPSG code, deprecated transformer, hallucinated API method name)
- [ ] You have a **behavioral observation** about tool-use patterns that isn't in any existing review (file reading, grounding, self-correction)
- [ ] Your timing numbers are **real wall-clock measurements**, not estimates
- [ ] Your recommendation is **scenario-specific**, not a blanket winner declaration

---

## 5. Next Steps

### Immediate Extensions

**Extend the benchmark with more GIS tasks:**
- GDAL/OGR command generation — ask both tools to write a `ogr2ogr` pipeline for a coordinate transformation + format conversion
- PostGIS query generation — spatial joins, ST_Within, raster operations
- QGIS PyQGIS scripting — processing algorithm chains

**Deepen the Gemini CLI tooling test:**
- Explore MCP (Model Context Protocol) server integration, which the source material identifies as supported for custom tool connections — this could enable direct FME Server API or Sentinel Hub API tool definitions
- Test Google Search grounding explicitly for "what is the current Sentinel-2 revisit time over my AOI?" — a factual spatial question where real-time grounding matters

**Automate the benchmark:**

```bash
# Sketch of a repeatable benchmark runner
for PROMPT_FILE in prompts/*.txt; do
    TASK=$(basename $PROMPT_FILE .txt)
    echo "Running: $TASK"
    
    time gemini < $PROMPT_FILE > results/gemini/${TASK}_output.txt 2>&1
    time claude < $PROMPT_FILE > results/claude/${TASK}_output.txt 2>&1
    
    echo "Completed: $TASK at $(date)"
done
```

### Publishing Your Tool Critic Piece

- **Your differentiator to emphasize:** GIS-specific hallucination patterns — general reviewers will never catch a hallucinated FME transformer name or a wrong Sentinel-2 band index
- **Platforms:** Your own site/newsletter > LinkedIn article > dev.to — the specificity plays best with a GIS/geospatial audience who will immediately recognize whether your test was rigorous
- **Include the raw outputs** as a linked Gist or repo so readers can verify your scoring — this separates a genuine benchmark from an opinion piece
- **Revisit quarterly:** Both CLIs are updating rapidly (Gemini CLI ships weekly stable releases per the source). A re-run in 90 days will show trajectory, which is more valuable than a single-point snapshot

### Integrate the Winner Into Your Workflow

If Gemini CLI scored competitively on your Sentinel Hub scripting tasks:

```bash
# Add a project-level alias so you can call both in parallel
alias gcli="gemini"
alias ccli="claude"

# Or: use Gemini CLI's free tier for exploratory/first-draft generation,
# Claude Code for refinement — a tiered workflow that costs you nothing
# on the Gemini side up to 1,000 requests/day
```

---

> **Source note:** All Gemini CLI commands, authentication flows, release channels, and feature descriptions in this tutorial are drawn directly from the [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) repository README. Non-interactive mode invocation via stdin piping is a standard shell pattern; if your installed version requires a specific flag, run `gemini --help` to confirm. Sentinel Hub API specifics (library methods, band names, configuration classes) reflect the `sentinelhub` Python library conventions — verify against the current [Sentinel Hub Python library documentation](https://sentinelhub-py.readthedocs.io/) before production use.