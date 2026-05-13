# Install everything-claude-code and Benchmark It Against Your Current Claude Code Setup

## Introduction & Context

### What Is This?

[everything-claude-code](https://github.com/affaan-m/everything-claude-code) is an **agent harness performance optimization system** for Claude Code CLI. Think of it as a structured scaffolding layer that sits on top of your existing Claude Code workflow, providing:

- **Skills** — reusable, named capability patterns Claude can invoke
- **Instincts** — persistent behavioral heuristics that guide autonomous decision-making
- **Memory architecture** — structured context that survives across sessions
- **Security guardrails** — constraints for safer autonomous execution
- **Research-first patterns** — forcing Claude to understand before acting

If you're already using `CLAUDE.md` to give Claude Code project context, this is the next level up: instead of one flat markdown file, you get a layered system where different types of knowledge live in different places, are loaded at different times, and compose in structured ways.

### Why It Matters for Python GIS Work

GIS projects are particularly good benchmarking targets because they involve:

- Multi-step spatial operations (load → transform → analyze → export) where **tool call efficiency matters**
- Heterogeneous file formats (shapefiles, GeoJSON, GeoTIFFs, PostGIS) that require **precise error recovery**
- Domain knowledge (CRS/projection handling, topology rules) where **instinct-level guidance** pays off
- Long-running processes where **memory persistence across sessions** is genuinely useful

A task like "reproject a shapefile and calculate zonal statistics" is simple enough to repeat, complex enough to show meaningful quality differences.

---

## Prerequisites

Before starting, confirm you have the following:

### Required Tools

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| Claude Code CLI | Latest | `claude --version` |
| Git | 2.x+ | `git --version` |
| Python | 3.10+ | `python --version` |
| `uv` or `pip` | Any recent | `uv --version` |

### Required Python Packages (in your GIS project)

```bash
# Core GIS stack — install if missing
pip install geopandas rasterio fiona shapely pyproj rasterstats
```

### Required Knowledge

- You've used Claude Code CLI at least once (run `claude` in a project directory)
- You have a working `CLAUDE.md` in at least one Python GIS project
- Basic comfort with shell scripting and `diff` tools

### Required Files

- **An active Python GIS project** with at least one substantive task you can describe in a single prompt (e.g., "reproject all shapefiles in `/data/raw` to EPSG:4326 and validate geometry")
- **Your existing `CLAUDE.md`** — you'll use this as the baseline

---

## Step-by-Step Guide

---

### Phase 1: Clone and Understand everything-claude-code

#### Step 1.1 — Clone the Repository

```bash
# Clone to a dedicated tools directory, not inside your GIS project
mkdir -p ~/tools/claude-harnesses
cd ~/tools/claude-harnesses
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
```

#### Step 1.2 — Map the Repository Structure

Before applying anything, understand what you're working with:

```bash
# Get a clear picture of the structure
find . -type f -name "*.md" | sort
find . -type f -name "*.json" | sort
find . -type f \( -name "*.yaml" -o -name "*.yml" \) | sort
ls -la
```

Spend 10 minutes reading the key files. Take notes on:

```bash
# Open each core file — read before copying anything
cat README.md
# Then navigate to any skills/, instincts/, or memory/ directories
ls -la */
```

> **🔍 What to look for:** Note which files are meant to go in your project root vs. a `.claude/` subdirectory vs. `~/.claude/`. Mixing these up is the most common setup mistake.

#### Step 1.3 — Document What You Find

Create a quick reference for yourself:

```bash
# Create a personal notes file
cat > ~/tools/claude-harnesses/MY_NOTES.md << 'EOF'
## everything-claude-code Structure Notes

### Files that go in PROJECT root:
- (fill in after reading)

### Files that go in PROJECT/.claude/:
- (fill in after reading)

### Files that go in ~/.claude/ (global):
- (fill in after reading)

### Key concepts I need to understand:
- Skills: 
- Instincts: 
- Memory: 
EOF
```

---

### Phase 2: Baseline — Record Your Current Setup

Before changing anything, lock in your baseline. This is what you'll compare against.

#### Step 2.1 — Archive Your Existing CLAUDE.md

```bash
# Navigate to your GIS project
cd /path/to/your/gis-project

# Archive the current state with a timestamp
cp CLAUDE.md CLAUDE.md.baseline-$(date +%Y%m%d)

# Also store it externally for the benchmark
mkdir -p ~/claude-benchmark/baseline
cp CLAUDE.md ~/claude-benchmark/baseline/CLAUDE.md
```

#### Step 2.2 — Define Your Benchmark Task

Pick **one concrete, repeatable task** from your GIS project. It should be:
- Completable in 2–5 minutes of Claude Code execution
- Verifiable (you can inspect the output programmatically)
- Representative of your real work

**Example benchmark tasks (pick one or write your own):**

```
TASK OPTION A — Reprojection + Validation:
"Find all shapefiles in data/raw/, reproject each one to EPSG:4326, 
save to data/processed/, and print a summary of: original CRS, 
new CRS, feature count, and whether geometry is valid for each file."

TASK OPTION B — Zonal Statistics:
"Load the raster at data/elevation.tif and the polygon shapefile at 
data/watersheds.shp. Calculate mean, min, max, and std elevation 
for each watershed polygon. Save results to data/watershed_stats.csv 
and print the top 5 watersheds by mean elevation."

TASK OPTION C — Data Quality Audit:
"Audit all GeoJSON files in data/. For each file report: CRS, 
geometry type, feature count, null field percentage per column, 
and any invalid geometries. Write a markdown report to reports/data_audit.md"
```

Write your chosen task into a file so it's identical each run:

```bash
mkdir -p ~/claude-benchmark
cat > ~/claude-benchmark/benchmark_task.txt << 'EOF'
[PASTE YOUR CHOSEN TASK HERE — EXACT WORDING]
EOF
```

#### Step 2.3 — Run the Baseline

```bash
# Navigate to your GIS project
cd /path/to/your/gis-project

# Start a fresh Claude Code session and run your task
# IMPORTANT: Note the start time
echo "BASELINE START: $(date)" >> ~/claude-benchmark/baseline/run_log.txt

claude  # Opens interactive session
```

Once inside Claude Code:

```
[paste the exact content of your benchmark_task.txt]
```

**While it runs, manually log in a separate terminal:**

```bash
# In a second terminal, watch and log tool calls
# (Claude Code shows tool calls in the UI — count them manually)

cat > ~/claude-benchmark/baseline/observations.md << 'EOF'
## Baseline Run Observations

**Date/Time:** 
**Task:** [task name]

### Metrics
- Total tool calls: 
- Read tool calls: 
- Write/Edit tool calls: 
- Bash tool calls: 
- Search/Grep calls: 
- Time to first useful output: 
- Total session duration: 

### Output Quality
- Did it complete the task? (yes/partial/no)
- Errors encountered: 
- Error recovery (describe): 
- Output correctness (verify manually): 

### Qualitative Notes
- Did it ask clarifying questions? 
- Did it seem to "understand" the GIS domain? 
- Did it make any avoidable mistakes? 
- Anything that felt inefficient? 

### Raw Output
[paste or describe the final output]
EOF
```

```bash
echo "BASELINE END: $(date)" >> ~/claude-benchmark/baseline/run_log.txt
```

#### Step 2.4 — Verify and Save Baseline Outputs

```bash
# Save whatever files Claude Code created
mkdir -p ~/claude-benchmark/baseline/outputs
cp -r data/processed/ ~/claude-benchmark/baseline/outputs/ 2>/dev/null || true
cp -r reports/ ~/claude-benchmark/baseline/outputs/ 2>/dev/null || true

# Reset the project state for the next run
# (undo whatever Claude Code wrote so you start fresh)
git checkout -- .  # if using git
# OR manually delete the outputs Claude created
```

---

### Phase 3: Apply the everything-claude-code Harness

#### Step 3.1 — Create the Harness Configuration for Your Project

Based on your notes from Phase 1, apply the relevant configuration. The exact structure depends on what's in the repo, but here's a generalized approach:

```bash
cd /path/to/your/gis-project

# Create the .claude directory structure if it doesn't exist
mkdir -p .claude/skills
mkdir -p .claude/instincts  
mkdir -p .claude/memory
```

#### Step 3.2 — Write a GIS-Specific Skills File

Skills are named, reusable capability descriptions. Create one tailored to your project:

```bash
cat > .claude/skills/gis_operations.md << 'EOF'
# GIS Operations Skills

## skill:reproject
When asked to reproject spatial data:
1. ALWAYS read the source CRS first with `python -c "import geopandas as gpd; print(gpd.read_file('FILE').crs)"`
2. Validate geometry before reprojecting with `.is_valid` check
3. Use `gdf.to_crs(epsg=TARGET)` — never use pyproj directly unless geopandas is unavailable
4. After reprojection, verify the output CRS matches target
5. Report: source CRS → target CRS, feature count, any invalid geometries fixed

## skill:validate_geometry
When validating spatial geometries:
1. Use `gdf.geometry.is_valid.all()` for a quick check
2. For invalid geometries, apply `gdf.geometry = gdf.geometry.buffer(0)` as first fix
3. Report count of invalid geometries found and fixed
4. Never silently drop features — log every dropped feature

## skill:format_detection
When encountering spatial files:
1. Detect format by extension: .shp/.dbf/.shx (Shapefile), .geojson/.json (GeoJSON), .gpkg (GeoPackage), .tif/.tiff (Raster)
2. For Shapefiles, check all companion files exist (.dbf, .shx, .prj)
3. Report encoding issues explicitly — common with older Shapefiles
4. Default encoding assumption: UTF-8, fallback to latin-1

## skill:crs_handling
CRS best practices for this project:
- Project standard CRS: [FILL IN YOUR PROJECT'S STANDARD CRS e.g., EPSG:4326]
- Always use EPSG codes, never WKT strings, in output summaries
- When CRS is None/missing, check the .prj file manually before assuming
- Log a WARNING if any file lacks a defined CRS
EOF
```

#### Step 3.3 — Write a GIS-Specific Instincts File

Instincts are persistent behavioral heuristics — things Claude should always or never do:

```bash
cat > .claude/instincts/gis_instincts.md << 'EOF'
# GIS Development Instincts

## ALWAYS
- Read before writing: inspect any spatial file before modifying or overwriting it
- Backup first: if modifying data in-place, copy the original to a `_backup` suffix first
- Check file size before loading: files >500MB should be chunked or streamed
- Use context managers: always use `with fiona.open()` or `with rasterio.open()` patterns
- Report CRS explicitly in every summary — never assume the user knows the source CRS
- Validate outputs: after any write operation, re-read and verify the file loads correctly

## NEVER
- Never overwrite raw data in `data/raw/` — always write to `data/processed/`
- Never use `gdf.to_file()` without specifying `driver` explicitly
- Never assume EPSG:4326 if CRS is not set — report it as unknown
- Never silently swallow exceptions in batch operations — log and continue

## RESEARCH FIRST
Before running any spatial operation:
1. Check what files actually exist: `ls -la data/`
2. Check file sizes: `du -sh data/*`
3. Sample the data: read first 5 rows/features before full processing
4. Confirm the CRS of ALL inputs before any transformation

## ERROR RECOVERY
When a spatial operation fails:
1. Check if the error is a missing dependency → `pip install <package>`
2. Check if the error is a CRS mismatch → reproject inputs to match
3. Check if the error is invalid geometry → apply buffer(0) fix
4. Check if the error is file format → try fiona.listlayers() to inspect
5. If all else fails, isolate the failing feature and report its properties
EOF
```

#### Step 3.4 — Write a Project Memory File

```bash
cat > .claude/memory/project_context.md << 'EOF'
# Project Memory: [YOUR PROJECT NAME]

## Data Architecture
- Raw data location: `data/raw/` — READ ONLY
- Processed output: `data/processed/`
- Reports: `reports/`
- Scripts: `scripts/`

## Key Files
[List your main data files here]
- `data/raw/[your file]`: [what it contains, CRS, feature count]

## Project Standards
- Standard output CRS: [YOUR CRS]
- Coordinate precision: 6 decimal places for geographic, 2 for projected
- File format for outputs: GeoPackage (.gpkg) preferred over Shapefile
- Attribute naming: snake_case, max 10 chars (Shapefile compatibility)

## Known Issues / Quirks
[Document any known data quality issues in your project]
- Example: watersheds.shp has 3 invalid geometries in the northeast region

## Dependencies
- Core: geopandas, rasterio, fiona, shapely, pyproj
- Analysis: rasterstats, scipy
- Viz: matplotlib, folium (optional)

## Session History
[Claude Code will append notes here across sessions]
EOF
```

#### Step 3.5 — Update Your CLAUDE.md to Load the Harness

Now integrate everything into a new `CLAUDE.md` that references the harness:

```bash
# Backup current CLAUDE.md first
cp CLAUDE.md CLAUDE.md.pre-harness

cat > CLAUDE.md << 'EOF'
# [YOUR PROJECT NAME] — Claude Code Configuration

## Agent Harness
This project uses the everything-claude-code harness pattern.
Load and apply all files in `.claude/` before beginning any task:
- `.claude/skills/gis_operations.md` — named GIS capabilities
- `.claude/instincts/gis_instincts.md` — behavioral constraints
- `.claude/memory/project_context.md` — persistent project state

## Project Overview
[Keep your existing project description here]

## Task Execution Protocol
1. **Research first**: Read relevant files and check what exists before writing code
2. **Apply skills**: Use named skills from `.claude/skills/` for standard operations
3. **Respect instincts**: Never violate constraints in `.claude/instincts/`
4. **Update memory**: After completing a task, append a brief note to `.claude/memory/project_context.md`

## Quick Reference
[Keep any quick-reference content from your original CLAUDE.md]
EOF
```

---

### Phase 4: Run the Harness Benchmark

#### Step 4.1 — Reset Project State

```bash
cd /path/to/your/gis-project

# Ensure you're starting from the same state as the baseline
git checkout -- .  # if using git, or manually reset outputs
# But keep the .claude/ directory and updated CLAUDE.md

# Verify your harness is in place
ls -la .claude/
ls -la .claude/skills/
ls -la .claude/instincts/
ls -la .claude/memory/
cat CLAUDE.md
```

#### Step 4.2 — Run the Harness Benchmark

```bash
# Note start time
echo "HARNESS START: $(date)" >> ~/claude-benchmark/harness/run_log.txt

claude  # Open a fresh Claude Code session
```

Use the **exact same prompt** from your `~/claude-benchmark/benchmark_task.txt`.

**Track the same metrics as baseline:**

```bash
cat > ~/claude-benchmark/harness/observations.md << 'EOF'
## Harness Run Observations

**Date/Time:** 
**Task:** [task name]

### Metrics
- Total tool calls: 
- Read tool calls: 
- Write/Edit tool calls: 
- Bash tool calls: 
- Search/Grep calls: 
- Time to first useful output: 
- Total session duration: 

### Output Quality
- Did it complete the task? (yes/partial/no)
- Errors encountered: 
- Error recovery (describe): 
- Output correctness (verify manually): 

### Qualitative Notes
- Did it apply skills from .claude/skills/? (which ones?)
- Did it respect instincts (research-first, no overwriting raw data)?
- Did it update memory at the end?
- Did it seem to "understand" the GIS domain better?
- Anything that felt more efficient vs. baseline?
- Anything that felt worse or over-constrained?

### Raw Output
[paste or describe the final output]
EOF
```

```bash
echo "HARNESS END: $(date)" >> ~/claude-benchmark/harness/run_log.txt
```

#### Step 4.3 — Save Harness Outputs

```bash
mkdir -p ~/claude-benchmark/harness/outputs
cp -r data/processed/ ~/claude-benchmark/harness/outputs/ 2>/dev/null || true
cp -r reports/ ~/claude-benchmark/harness/outputs/ 2>/dev/null || true
cp .claude/memory/project_context.md ~/claude-benchmark/harness/ 2>/dev/null || true
```

---

### Phase 5: Compare and Analyze

#### Step 5.1 — Quantitative Comparison

```bash
# Create a comparison summary
cat > ~/claude-benchmark/COMPARISON.md << 'EOF'
# Benchmark Comparison: Baseline vs. everything-claude-code Harness

## Task
[task description]

## Quantitative Metrics

| Metric | Baseline | Harness | Delta |
|--------|----------|---------|-------|
| Total tool calls | | | |
| Read tool calls | | | |
| Write/Edit tool calls | | | |
| Bash tool calls | | | |
| Time to first useful output | | | |
| Total session duration | | | |
| Task completion | | | |
| Errors encountered | | | |

## Output Quality Comparison

| Dimension | Baseline | Harness | Notes |
|-----------|----------|---------|-------|
| Correctness | /5 | /5 | |
| Completeness | /5 | /5 | |
| GIS domain accuracy | /5 | /5 | |
| Error recovery quality | /5 | /5 | |
| Code quality | /5 | /5 | |

## Qualitative Findings

### What the harness improved:
- 

### What the harness didn't change:
- 

### What the harness made worse (if anything):
- 

### Unexpected behaviors:
- 

## Verdict
[ ] Harness clearly better — adopt it
[ ] Harness slightly better — worth the setup cost
[ ] No meaningful difference for this task type
[ ] Baseline better — harness was over-constrained
EOF
```

#### Step 5.2 — Diff the Outputs Programmatically

```bash
# Compare outputs if they're text-based (CSV, GeoJSON, markdown reports)
diff ~/claude-benchmark/baseline/outputs/ ~/claude-benchmark/harness/outputs/ -r --brief

# For GeoJSON, compare feature counts
python3 << 'EOF'
import json
import os

baseline_dir = os.path.expanduser("~/claude-benchmark/baseline/outputs")
harness_dir = os.path.expanduser("~/claude-benchmark/harness/outputs")

for dirpath, _, files in os.walk(baseline_dir):
    for f in files:
        if f.endswith('.geojson'):
            baseline_file = os.path.join(dirpath, f)
            harness_file = baseline_file.replace(baseline_dir, harness_dir)
            if os.path.exists(harness_file):
                with open(baseline_file) as b, open(harness_file) as h:
                    bf = json.load(b)
                    hf = json.load(h)
                    b_count = len(bf.get('features', []))
                    h_count = len(hf.get('features', []))
                    match = "✓" if b_count == h_count else "✗ MISMATCH"
                    print(f"{match} {f}: baseline={b_count} features, harness={h_count} features")
EOF
```

#### Step 5.3 — Validate CRS Consistency of Both Outputs

```bash
python3 << 'EOF'
import geopandas as gpd
import os

for label, base in [
    ("BASELINE", os.path.expanduser("~/claude-benchmark/baseline/outputs")),
    ("HARNESS", os.path.expanduser("~/claude-benchmark/harness/outputs"))
]:
    print(f"\n=== {label} ===")
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(('.shp', '.geojson', '.gpkg')):
                path = os.path.join(root, f)
                try:
                    gdf = gpd.read_file(path)
                    valid_pct = gdf.geometry.is_valid.mean() * 100
                    print(f"  {f}: CRS={gdf.crs}, features={len(gdf)}, valid_geometry={valid_pct:.1f}%")
                except Exception as e:
                    print(f"  {f}: ERROR — {e}")
EOF
```

---

### Phase 6: Write Your Tool Critic Review

A Tool Critic review is a structured, honest assessment meant to help others make informed adoption decisions.

```bash
cat > ~/claude-benchmark/TOOL_CRITIC_REVIEW.md << 'EOF'
# Tool Critic Review: everything-claude-code

**Reviewer:** [Your name]  
**Date:** [Date]  
**Review Type:** Benchmarked against personal baseline  
**Project Type:** Python GIS (geopandas/rasterio stack)  
**Task Tested:** [Task description]

---

## Setup Experience

**Time to configure:** ~__ minutes  
**Difficulty:** Easy / Moderate / Hard  
**Documentation quality:** /5  

**Friction points encountered:**
- 

**What was clear:**
- 

---

## Performance Results

[Paste your comparison table from COMPARISON.md]

---

## What This Changes About Your Workflow

### The Genuine Wins
[Be specific — "Claude no longer overwrites raw data" is better than "it follows instincts"]

### The Genuine Costs
[Setup time, maintenance burden, over-constraint, etc.]

### GIS-Specific Observations
[Anything domain-specific worth noting for other GIS developers]

---

## Patterns Worth Stealing (Even Without Full Adoption)

If you don't want the whole harness, these specific patterns are worth copying:

1. **[Pattern name]**: [What it is and why it helps]
2. **[Pattern name]**: [What it is and why it helps]
3. **[Pattern name]**: [What it is and why it helps]

---

## Recommendation

**For GIS developers with established CLAUDE.md setups:**
[ ] Adopt immediately
[ ] Adopt the memory/instincts pattern, skip skills
[ ] Adopt for complex projects, skip for exploratory work  
[ ] Skip — maintenance cost exceeds benefit
[ ] Skip — better alternatives exist (specify: ___)

**One-sentence verdict:**
> [Your honest, specific verdict]

---

## What I'd Improve in the Harness

[Constructive suggestions for the repo maintainer]
EOF
```

---

## Validation

You've successfully completed this exercise if you can check off all of the following:

### Setup Validation

```bash
# Run this checklist
echo "=== Harness Setup Validation ===" 
echo ""

GIS_PROJECT="/path/to/your/gis-project"  # update this

[ -f "$GIS_PROJECT/CLAUDE.md" ] && echo "✓ CLAUDE.md present" || echo "✗ CLAUDE.md missing"
[ -f "$GIS_PROJECT/CLAUDE.md.baseline-"* ] && echo "✓ Baseline CLAUDE.md archived" || echo "✗ Baseline not archived"
[ -d "$GIS_PROJECT/.claude/skills" ] && echo "✓ skills/ directory present" || echo "✗ skills/ missing"
[ -d "$GIS_PROJECT/.claude/instincts" ] && echo "✓ instincts/ directory present" || echo "✗ instincts/ missing"
[ -d "$GIS_PROJECT/.claude/memory" ] && echo "✓ memory/ directory present" || echo "✗ memory/ missing"
[ -f ~/claude-benchmark/baseline/observations.md ] && echo "✓ Baseline run documented" || echo "✗ Baseline not documented"
[ -f ~/claude-benchmark/harness/observations.md ] && echo "✓ Harness run documented" || echo "✗ Harness not documented"
[ -f ~/claude-benchmark/COMPARISON.md ] && echo "✓ Comparison written" || echo "✗ Comparison missing"
[ -f ~/claude-benchmark/TOOL_CRITIC_REVIEW.md ] && echo "✓ Tool Critic review written" || echo "✗ Review missing"
```

### Content Validation

Your exercise is complete when:

1. **Both runs used identical prompts** — the task text was copy-pasted, not retyped
2. **Both runs started from identical project state** — same input files, same directory structure
3. **You tracked tool calls in both runs** — even rough counts (±2) are valuable
4. **You verified output correctness** — ran the Python validation scripts in Phase 5
5. **Your Tool Critic review contains at least one specific, falsifiable claim** — e.g., "The harness reduced tool calls by ~30% on reprojection tasks" not "it seemed better"

---

## Next Steps

### Immediate (This Week)

- **Share your Tool Critic review** — post it where other Claude Code users can find it (a team channel, a gist, a PR to the everything-claude-code repo)
- **Run a second benchmark task** — pick a different task type (e.g., if you tested reprojection, now test data quality audit) to see if results generalize
- **Refine your instincts file** — after one real session with the harness, you'll have opinions about what constraints are wrong or missing

### Short Term (Next Month)

- **Build a skills library for your domain** — if you work with specific data sources (OpenStreetMap, NOAA datasets, Census TIGER files), write skills for those specific patterns
- **Experiment with memory structure** — try having Claude Code maintain a running `session_log.md` and see if it actually helps on multi-session tasks
- **Test on a longer task** — the benchmark above was short; try a task that takes 15–30 minutes of Claude Code work to see if harness benefits compound

### Longer Term

- **Contribute back to everything-claude-code** — if you wrote GIS-specific skills that work well, open a PR or post them as a gist and reference from the repo discussions
- **Compare with other harness approaches** — look at how other `CLAUDE.md` systems structure persistent context (Simon Willison's approach, the Anthropic official examples) and triangulate what actually works
- **Automate the benchmark** — write a shell script that resets project state, runs Claude Code non-interactively with a fixed prompt, and captures output to a file so you can benchmark multiple harness variations without manual effort

### Resources

- [Claude Code CLI Documentation](https://docs.anthropic.com/en/docs/claude-code) — official reference
- [everything-claude-code Repo](https://github.com/affaan-m/everything-claude-code) — upstream source
- [GeoPandas Documentation](https://geopandas.org/) — for validating GIS output correctness
- [Rasterio Documentation](https://rasterio.readthedocs.io/) — for raster operation validation

---

> **A note on honest benchmarking:** The most valuable outcome of this exercise isn't proving the harness is better — it's developing a *methodology* for evaluating any Claude Code configuration change. The discipline of identical prompts, logged tool calls, and verified outputs will serve you every time you're deciding whether a new `CLAUDE.md` pattern is worth adopting.