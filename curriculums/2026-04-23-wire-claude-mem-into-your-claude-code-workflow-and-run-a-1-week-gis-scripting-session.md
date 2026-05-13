# Wire `claude-mem` into Your Claude Code Workflow: A 1-Week GIS Scripting Session Guide

## Introduction & Context

If you've spent any time with Claude Code on multi-session projects — like migrating FME workspaces to Python — you've felt the pain: every new session starts cold. You re-explain your coordinate reference systems, re-paste your FME transformer logic, re-clarify why you're using `geopandas` over `arcpy`. It's a productivity tax that compounds daily.

**`claude-mem`** is a Claude Code plugin built by [@thedotmack](https://github.com/thedotmack) that solves this. It:

- **Auto-captures** meaningful activity from each Claude Code session
- **Compresses** that activity using AI into dense, reusable context snippets
- **Injects** relevant context automatically when you start future sessions

For a GIS developer mid-migration from FME to Python, this means Claude remembers your spatial data schemas, your preferred `shapely` patterns, your CRS conventions, and your project-specific quirks — without you lifting a finger.

**Why this matters for your workflow specifically:**
- Your `CLAUDE.md` may be carrying dead weight — repeated context that `claude-mem` can handle dynamically
- FME-to-Python migrations are multi-week efforts with deeply stateful context (transformer equivalents, workspace logic, data pipeline decisions)
- Agentic sessions benefit enormously from memory continuity — fewer corrections, faster iteration

---

## Prerequisites

Before starting, confirm you have the following in place:

### Required
- [ ] **Claude Code CLI** installed and authenticated (`claude --version` returns a version)
- [ ] **Node.js** v18+ (`node --version`)
- [ ] **npm** or **npx** available in your PATH
- [ ] An active **FME-to-Python migration project** with at least one Python script or workspace to work from
- [ ] A working `CLAUDE.md` file in your project root (even a rough one)
- [ ] Git initialized in your project (`git init` if not already)

### Helpful but not required
- [ ] Basic familiarity with Claude Code slash commands (e.g., `/project`, `/help`)
- [ ] Existing session logs or notes from prior Claude Code sessions

### Environment check
Run these to confirm your setup before proceeding:

```bash
# Check Claude Code
claude --version

# Check Node
node --version  # Should be 18+

# Check you're in a git repo (claude-mem uses git context)
git status

# Check your CLAUDE.md exists
ls -la CLAUDE.md
```

---

## Step-by-Step Guide

### Phase 1: Installation (Day 1 — ~20 minutes)

#### Step 1.1 — Clone and Install `claude-mem`

```bash
# Option A: Install globally via npm (recommended)
npm install -g claude-mem

# Option B: Use npx without installing
npx claude-mem --help

# Verify installation
claude-mem --version
```

> **Note:** If the npm package name differs from the repo, install directly from source:

```bash
git clone https://github.com/thedotmack/claude-mem.git
cd claude-mem
npm install
npm link  # Makes `claude-mem` available globally
```

#### Step 1.2 — Initialize `claude-mem` in Your Project

Navigate to your GIS migration project root and initialize:

```bash
cd /path/to/your/fme-to-python-project
claude-mem init
```

This creates a `.claude-mem/` directory in your project. Inspect what it generates:

```bash
ls -la .claude-mem/
# Expect: config.json, sessions/, memory/
cat .claude-mem/config.json
```

#### Step 1.3 — Configure for GIS Context

Edit `.claude-mem/config.json` to tune the plugin for your use case. Add any project-specific capture hints:

```json
{
  "project": "fme-to-python-migration",
  "capturePatterns": [
    "*.py",
    "*.fmw",
    "*.geojson",
    "*.gpkg"
  ],
  "contextHints": [
    "FME transformer equivalents",
    "CRS and projection handling",
    "geopandas workflows",
    "spatial data schemas"
  ],
  "compressionLevel": "high",
  "injectOnStart": true
}
```

> **Adjust based on actual config schema** — check `claude-mem --help` or the repo README for the exact keys your installed version supports.

#### Step 1.4 — Add `.claude-mem/sessions/` to `.gitignore`

Keep raw session logs out of your repo (the compressed memory is fine to commit):

```bash
echo ".claude-mem/sessions/" >> .gitignore
echo "# claude-mem compressed memory (safe to commit)" >> .gitignore
echo "# .claude-mem/memory/" >> .gitignore
git add .gitignore
git commit -m "chore: add claude-mem, ignore raw sessions"
```

---

### Phase 2: Baseline — Your First Instrumented Session (Day 1-2)

#### Step 2.1 — Document Your Starting `CLAUDE.md`

Before `claude-mem` changes anything, snapshot your current `CLAUDE.md` length and content. This is your baseline:

```bash
wc -l CLAUDE.md  # Line count
wc -w CLAUDE.md  # Word count
cp CLAUDE.md CLAUDE.md.baseline  # Save baseline
```

Create a simple log file to track your weekly observations:

```bash
cat > claude-mem-findings.md << 'EOF'
# claude-mem Findings Log

## Baseline (Day 1)
- CLAUDE.md line count: [FILL IN]
- CLAUDE.md word count: [FILL IN]
- Known pain points re-injected manually each session:
  - [ ] Project CRS (e.g., EPSG:4326 → EPSG:27700)
  - [ ] FME workspace being migrated: [NAME]
  - [ ] Python environment / dependency choices
  - [ ] Data schema field names
  - [ ] [Add your own]

## Sessions
EOF
```

#### Step 2.2 — Run Your First Session WITH `claude-mem`

Start Claude Code with `claude-mem` active:

```bash
# Start claude-mem listener (if it runs as a background process)
claude-mem start

# Then launch Claude Code as normal
claude
```

> **Depending on how `claude-mem` integrates**, it may wrap Claude Code directly:
> ```bash
> claude-mem run claude
> # or
> claude-mem exec -- claude
> ```
> Check `claude-mem --help` for the exact invocation.

#### Step 2.3 — Run a Real FME-to-Python Task

Inside your Claude Code session, work on an actual migration task. Here's an example prompt to get productive output that's worth capturing:

```
I'm migrating an FME workspace to Python. The workspace does the following:
1. Reads a shapefile of UK local authority boundaries (EPSG:27700)
2. Uses a Clipper transformer to extract features within a bounding box
3. Reprojects to EPSG:4326
4. Writes to GeoJSON

Help me write the equivalent Python script using geopandas. 
My shapefile is at: data/raw/local_authority_boundaries.shp
Output should go to: data/processed/clipped_boundaries.geojson
```

Work through 2-3 meaningful exchanges — ask follow-up questions, refine the script, debug edge cases. This gives `claude-mem` substantive material to capture.

#### Step 2.4 — Close the Session and Review Capture

End your Claude Code session, then check what `claude-mem` captured:

```bash
# End the session
claude-mem stop  # or it may auto-capture on session end

# Review what was captured
claude-mem status
claude-mem show --last

# See the compressed memory
cat .claude-mem/memory/latest.md
```

Log your observations:

```bash
cat >> claude-mem-findings.md << 'EOF'

## Session 1 — [DATE]
**Task:** FME Clipper → geopandas clip migration
**Duration:** [X] minutes
**What claude-mem captured:**
- [Copy key items from .claude-mem/memory/latest.md]

**What it MISSED that I'd want remembered:**
- 

**Manual context I still had to provide:**
- 
EOF
```

---

### Phase 3: The 5-Session Experiment (Days 2-6)

Run at least 5 sessions across the week. Here's a suggested session plan for a GIS migration project:

#### Suggested Session Topics

| Session | Day | FME Transformer Focus | Python/GIS Equivalent |
|---------|-----|----------------------|----------------------|
| 1 | 1-2 | Clipper + Reprojector | `geopandas.clip()` + `.to_crs()` |
| 2 | 2-3 | AttributeFilter + Tester | Boolean masks + `.loc[]` filtering |
| 3 | 3-4 | Joiner (spatial join) | `geopandas.sjoin()` |
| 4 | 4-5 | Aggregator + StatisticsCalculator | `.dissolve()` + `.agg()` |
| 5 | 5-6 | FeatureWriter (multiple formats) | Format-aware write abstraction |

#### Step 3.1 — Starting Each Session (The Test)

For sessions 2-5, **deliberately do NOT manually re-inject your usual context**. Let `claude-mem` do the work:

```bash
# Start fresh session
claude-mem start
claude

# In the session, begin with a COLD prompt:
# "Continue the FME to Python migration."
# 
# Observe: Does Claude already know your project context?
# Does it remember your CRS? Your file paths? Your style preferences?
```

After each session, rate the auto-injected context quality (0-5):

```bash
cat >> claude-mem-findings.md << 'EOF'

## Session [N] — [DATE]
**Task:** [FME transformer being migrated]
**Auto-injected context quality (0-5):** 
**Context it correctly remembered:**
- 
**Context gaps (still had to manually provide):**
- 
**Useful new patterns claude-mem captured:**
- 
EOF
```

#### Step 3.2 — Sample GIS Scripts to Run Across Sessions

Use these as your session material — they build on each other, which is a good test of memory continuity:

**Session 2 — Attribute filtering:**
```python
# Prompt Claude to help you build this, then let claude-mem capture the decisions
import geopandas as gpd

def filter_by_attribute(gdf, field, values, operator='eq'):
    """
    FME AttributeFilter equivalent.
    
    Args:
        gdf: GeoDataFrame
        field: field name to filter on  
        values: list of accepted values
        operator: 'eq', 'gt', 'lt', 'contains'
    """
    if operator == 'eq':
        return gdf[gdf[field].isin(values)]
    elif operator == 'contains':
        return gdf[gdf[field].str.contains('|'.join(values), na=False)]
    # Add operators as needed
    raise ValueError(f"Unsupported operator: {operator}")
```

**Session 3 — Spatial join:**
```python
# Ask Claude to help translate FME Joiner behavior
def spatial_join_with_fallback(left_gdf, right_gdf, how='left', predicate='intersects'):
    """
    FME SpatialFilter/Joiner equivalent.
    Handles CRS mismatch automatically — a lesson from Session 1.
    """
    if left_gdf.crs != right_gdf.crs:
        right_gdf = right_gdf.to_crs(left_gdf.crs)
    
    return gpd.sjoin(left_gdf, right_gdf, how=how, predicate=predicate)
```

**Session 4 — Dissolve and aggregate:**
```python
# FME Aggregator equivalent
def dissolve_with_stats(gdf, dissolve_by, agg_fields):
    """
    FME Aggregator equivalent.
    
    Args:
        dissolve_by: field to dissolve on (FME: Group By)
        agg_fields: dict of {field: aggregation_func}
                    e.g., {'population': 'sum', 'name': 'first'}
    """
    return gdf.dissolve(by=dissolve_by, aggfunc=agg_fields).reset_index()
```

---

### Phase 4: Evaluation and Write-Up (Day 7)

#### Step 4.1 — Quantitative Audit

At the end of the week, measure the impact:

```bash
# Current CLAUDE.md
wc -l CLAUDE.md
wc -w CLAUDE.md

# Memory stored by claude-mem
claude-mem stats  # If available
ls -la .claude-mem/memory/
wc -l .claude-mem/memory/*.md

# What's been auto-captured
claude-mem show --all
```

Fill in this comparison table in your findings:

```markdown
## Week Summary — Quantitative

| Metric | Before | After |
|--------|--------|-------|
| CLAUDE.md line count | [BASELINE] | [CURRENT] |
| CLAUDE.md word count | [BASELINE] | [CURRENT] |
| Manual context re-injections/session | ~[N] | ~[N] |
| Avg session ramp-up time (estimate) | [N] min | [N] min |
| claude-mem memory entries captured | 0 | [N] |
```

#### Step 4.2 — Prune Your `CLAUDE.md`

Based on what `claude-mem` is reliably capturing, identify which sections of `CLAUDE.md` can be removed or shortened:

```bash
# Open both side by side
code CLAUDE.md .claude-mem/memory/latest.md
```

Look for overlaps. Common candidates for removal from `CLAUDE.md`:
- File path conventions (captured from session activity)
- CRS preferences (captured from code patterns)
- Dependency choices (captured from imports and installs)
- Naming conventions (captured from your code style)

**Keep in `CLAUDE.md`:**
- High-level project goals
- Constraints that aren't inferrable from code (business rules, data sensitivity)
- Architectural decisions
- Things you want Claude to *never* do

```bash
# Diff original vs trimmed
diff CLAUDE.md.baseline CLAUDE.md
```

#### Step 4.3 — Write Your Findings for The Build Pillar

Use this template to structure your write-up:

```markdown
# claude-mem Review: 1-Week GIS Scripting Trial

## TL;DR
[2-3 sentence summary of whether it's worth it]

## Setup Experience
- Installation friction: [Low/Medium/High]
- Configuration required: [describe]
- Integration with Claude Code: [seamless/requires workaround/broken]

## What It Captured Well
- [Specific examples from your sessions]

## What It Missed
- [Gaps you still had to fill manually]

## Impact on CLAUDE.md
- Before: [N] lines / [N] words
- After: [N] lines / [N] words  
- Reduction: [%]
- Sections removed: [list]

## GIS-Specific Observations
- [Did it handle spatial/domain context well?]
- [Any FME-specific terminology handled correctly?]

## Recommendation
[ ] Adopt permanently
[ ] Adopt with modifications
[ ] Skip — not worth the overhead

## If Adopting: Suggested Config
[Paste your working config.json]
```

---

## Validation

You've successfully completed this exercise if you can check off all of the following:

### Installation ✓
- [ ] `claude-mem --version` returns a version number
- [ ] `.claude-mem/` directory exists in your project root
- [ ] `.claude-mem/sessions/` is in your `.gitignore`

### Usage ✓
- [ ] Completed 5+ Claude Code sessions with `claude-mem` running
- [ ] Each session covered a real FME-to-Python migration task
- [ ] `.claude-mem/memory/` contains at least 3 compressed session entries

### Evaluation ✓
- [ ] You have a before/after word count for `CLAUDE.md`
- [ ] You can name at least 2 things `claude-mem` captured correctly without prompting
- [ ] You can name at least 1 gap where it fell short
- [ ] You have a written recommendation (adopt / modify / skip)

### The Build Pillar Write-Up ✓
- [ ] Findings document exists with quantitative metrics
- [ ] At least one "GIS-specific observation" is recorded
- [ ] You have a clear verdict on whether this reduces `CLAUDE.md` length meaningfully

---

## Troubleshooting

### `claude-mem` doesn't seem to inject context on session start

```bash
# Check if the plugin is actually hooking into Claude Code
claude-mem status
claude-mem doctor  # If available

# Manual injection fallback
claude-mem show --last | pbcopy  # Copy to clipboard
# Then paste at the start of your Claude session manually
```

### Context captured is too generic / not GIS-specific

Edit your config to increase specificity hints and reduce noise:

```json
{
  "contextHints": [
    "geopandas",
    "shapely",
    "FME transformer",
    "EPSG CRS codes",
    "spatial join",
    "coordinate reference system"
  ],
  "minRelevanceScore": 0.7
}
```

### Sessions aren't being captured

```bash
# Ensure you're ending sessions cleanly
claude-mem stop  # Don't just close the terminal

# Or set up auto-capture on exit
claude-mem config --set autoCapture=true
```

---

## Next Steps

Once you've completed the 1-week trial and written your findings, here's where to take this further:

### Immediate (Week 2)
1. **Share your findings** — Post your write-up to The Build pillar; your config and observations are genuinely useful to others running similar workflows
2. **Refine your config** — Based on gaps identified, tune `claude-mem`'s capture patterns specifically for GIS work
3. **Trim `CLAUDE.md` aggressively** — If `claude-mem` is working, your `CLAUDE.md` should get shorter and more strategic, not longer

### Extend the Experiment
4. **Test across project boundaries** — Does `claude-mem` help when switching between the FME migration project and a separate analysis project? Or does it bleed context incorrectly?
5. **Contribute upstream** — If you find GIS-specific capture improvements, open a PR or issue at [github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)

### Broader Workflow Integration
6. **Pair with a structured `CLAUDE.md` template** — Your trimmed post-experiment `CLAUDE.md` could become the template for future GIS projects
7. **Explore other Claude Code plugins** — The ecosystem is young; `claude-mem` is one of the first memory-layer plugins, but not the last

### The Bigger Picture
8. **Document your FME-to-Python patterns** — The transformer equivalents you've built across 5+ sessions are now partly in `claude-mem`. Extract them into a standalone `FME_EQUIVALENTS.md` reference — this is institutional knowledge worth making explicit
9. **Evaluate against alternatives** — Compare `claude-mem`'s automatic approach against manually maintained session notes or a structured `scratchpad.md` — your week of data gives you an honest basis for comparison

---

*This curriculum was designed for a 1-week, low-effort trial. The goal isn't perfection — it's honest data on whether automatic session memory earns its place in your agentic development stack.*