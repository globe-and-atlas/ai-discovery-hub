# Audit Your CLAUDE.md Against the everything-claude-code Harness Patterns

## A Practical Curriculum for GIS Automation Workflow Optimization

---

## 1. Introduction & Context

### What This Is

Your `CLAUDE.md` file is the instruction layer that shapes how Claude Code behaves in your projects — it defines conventions, constraints, and workflows that Claude follows autonomously. Most practitioners start with a minimal `CLAUDE.md` and grow it organically, which often leaves significant performance on the table.

The **everything-claude-code** repository (by affaan-m) is a battle-tested agent harness that systematically extends Claude Code with five structured layers:

| Layer | Purpose |
|---|---|
| **Skills** | Reusable capability modules Claude can invoke |
| **Instincts** | Default behavioral heuristics and decision rules |
| **Persistent Memory** | Cross-session context and project state retention |
| **Security** | Guardrails against destructive or unintended actions |
| **Research-First Patterns** | Structured exploration before implementation |

### Why This Matters for GIS Automation

GIS workflows sit at the intersection of spatial data complexity, file system operations, external API calls (tile servers, geocoders, WFS/WMS endpoints), and often destructive operations (overwriting shapefiles, dropping PostGIS tables, bulk raster processing). This makes them a **high-value, high-risk** domain for agentic AI — exactly the environment where structured harness patterns pay the biggest dividends.

By auditing your current `CLAUDE.md` against the everything-claude-code patterns, you will:

- Identify capability gaps that are slowing down your GIS automation loops
- Adopt security guardrails appropriate for spatial data pipelines
- Create documented delta analysis suitable for publication as a **Globe & Atlas Tool Critic** post

---

## 2. Prerequisites

Before starting this exercise, confirm you have the following in place:

### Technical Requirements

```bash
# Verify Claude Code CLI is installed
claude --version
# Expected: claude 1.x.x or higher

# Verify Git is available
git --version

# Verify Python (for GIS workflow context)
python --version
# Expected: 3.10+

# Optional but recommended: GDAL/OGR for GIS validation steps
gdal-config --version
```

### Knowledge Prerequisites

- [ ] You have an existing `CLAUDE.md` file in at least one GIS project directory
- [ ] You have used Claude Code CLI for at least one automation task
- [ ] You understand basic Markdown formatting
- [ ] You are familiar with at least one of: QGIS automation, GeoPandas, PostGIS, GDAL/OGR, or similar GIS tooling
- [ ] You have a GitHub account (to fork/clone the repo)

### File System Prerequisites

```bash
# Create a working directory for this exercise
mkdir -p ~/claude-audit-exercise
cd ~/claude-audit-exercise

# Locate your existing CLAUDE.md files
find ~ -name "CLAUDE.md" -not -path "*/node_modules/*" 2>/dev/null
```

> **Note:** If you don't have an existing `CLAUDE.md`, use the scaffold provided in Step 3.1 below.

---

## 3. Step-by-Step Guide

---

### Step 3.1 — Clone and Inventory the everything-claude-code Repository

```bash
# Clone the repository
cd ~/claude-audit-exercise
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code

# Get a high-level directory inventory
find . -type f -name "*.md" | sort
find . -type f -name "*.json" | sort
find . -type f -name "*.py" | sort

# Review the root CLAUDE.md immediately
cat CLAUDE.md
```

Open a dedicated notes file for your audit:

```bash
touch ~/claude-audit-exercise/audit-notes.md
cat > ~/claude-audit-exercise/audit-notes.md << 'EOF'
# CLAUDE.md Audit Notes
Date: $(date +%Y-%m-%d)
Auditor: [Your Name]

## everything-claude-code Patterns Observed
(fill as you read)

## My Current CLAUDE.md Gaps
(fill as you compare)

## 3 Adopted Patterns for GIS Workflows
(fill in Step 3.5)

## Delta Summary for Globe & Atlas Post
(fill in Step 3.6)
EOF
```

---

### Step 3.2 — Extract and Categorize the Five Harness Layers

Work through each layer systematically. For each one, read the source files and extract the **core pattern** — the repeatable structure or directive format.

#### 3.2a — Skills Layer

```bash
# Explore the skills directory (adjust path based on actual repo structure)
ls -la skills/ 2>/dev/null || find . -path "*/skills*" -type f

# Read each skill definition
for f in skills/*.md skills/*.json 2>/dev/null; do
  echo "=== $f ==="
  cat "$f"
  echo ""
done
```

In your audit notes, answer:

```markdown
## Skills Layer Questions
- What is the format for defining a skill? (YAML front matter? JSON? Inline markdown?)
- Are skills invoked by name, by trigger phrase, or automatically?
- What skills are domain-general vs. task-specific?
- Which skills have NO equivalent in my current CLAUDE.md?
```

#### 3.2b — Instincts Layer

```bash
# Explore instincts
find . -path "*/instinct*" -type f | xargs ls -la 2>/dev/null
cat instincts/*.md 2>/dev/null || find . -name "*instinct*" -exec cat {} \;
```

Look specifically for:

- **Decision tree patterns** — how Claude is told to choose between approaches
- **Default behavior overrides** — what Claude does when instructions are ambiguous
- **Escalation triggers** — when Claude stops and asks rather than acts

Record patterns in this format:

```markdown
### Instinct Pattern Template
- **Trigger condition:** [what situation activates this instinct]
- **Default behavior:** [what Claude does without the instinct]
- **Modified behavior:** [what Claude does WITH the instinct]
- **GIS relevance:** [high/medium/low — why]
```

#### 3.2c — Persistent Memory Layer

```bash
# Explore memory structures
find . -path "*/memory*" -type f | xargs cat 2>/dev/null
find . -name "*.json" | xargs grep -l "memory\|context\|session" 2>/dev/null
```

Key things to look for:

```bash
# Does the harness use a memory file pattern?
grep -r "memory_file\|MEMORY\|remember\|recall" . --include="*.md" -l

# Does it reference a project state structure?
grep -r "project_state\|last_session\|checkpoint" . --include="*.md" -l
```

#### 3.2d — Security Layer

```bash
# This is critical for GIS work — explore thoroughly
find . -path "*/security*" -type f | xargs cat 2>/dev/null
grep -r "never\|always\|forbidden\|prohibited\|confirm\|destructive" . \
  --include="*.md" -n
```

Create a security pattern inventory:

```markdown
## Security Patterns Found
| Pattern Type | Trigger | Action Required | GIS Equivalent |
|---|---|---|---|
| File deletion guard | rm, delete, drop | Explicit confirmation | Shapefile deletion, DROP TABLE |
| Overwrite protection | write, save, export | Backup check | Overwriting GeoTIFF/GPKG |
| API rate limiting | external request | Throttle + log | Geocoding APIs, WFS calls |
| Schema validation | before DB write | Validate types | PostGIS geometry validation |
```

#### 3.2e — Research-First Patterns

```bash
# Find the research-first directives
grep -r "research\|explore\|understand\|read.*first\|before.*implement" . \
  --include="*.md" -n | head -40
```

The research-first pattern typically looks like this in `CLAUDE.md` files:

```markdown
# Example research-first directive (adapt from repo)
Before implementing any solution:
1. Read existing code in the affected directory
2. Identify existing patterns and conventions
3. Check for existing utilities that solve the problem
4. Propose approach and get confirmation before writing code
```

---

### Step 3.3 — Audit Your Existing CLAUDE.md

Now compare your current file against what you've found.

```bash
# Copy your primary CLAUDE.md into the working directory
cp /path/to/your/project/CLAUDE.md ~/claude-audit-exercise/my-current-claude.md

# If you don't have one yet, create a minimal starting scaffold:
cat > ~/claude-audit-exercise/my-current-claude.md << 'EOF'
# Project CLAUDE.md (Starting Scaffold)

## Project Overview
GIS automation project using [YOUR TOOLS HERE].

## Commands
- Run tests: `pytest tests/`
- Lint: `ruff check .`
- Process data: `python pipeline.py`

## Conventions
- Use GeoPandas for vector operations
- Store outputs in /outputs directory
- CRS: EPSG:4326 unless otherwise specified
EOF
```

Run a structured gap analysis:

```bash
# Create the gap analysis file
cat > ~/claude-audit-exercise/gap-analysis.md << 'EOF'
# CLAUDE.md Gap Analysis

## Layer Coverage Assessment

| Layer | everything-claude-code | My CLAUDE.md | Gap Severity |
|---|---|---|---|
| Skills | ✅ Defined | ❌/⚠️/✅ | HIGH/MED/LOW |
| Instincts | ✅ Defined | ❌/⚠️/✅ | HIGH/MED/LOW |
| Persistent Memory | ✅ Defined | ❌/⚠️/✅ | HIGH/MED/LOW |
| Security Guards | ✅ Defined | ❌/⚠️/✅ | HIGH/MED/LOW |
| Research-First | ✅ Defined | ❌/⚠️/✅ | HIGH/MED/LOW |

## Specific Missing Directives
(list each directive from the harness that has no equivalent in your file)

## Partially Covered Areas
(list directives where you have something similar but less rigorous)

## Areas Where You Exceed the Harness
(list GIS-specific directives the harness doesn't cover)
EOF
```

Use this checklist as you audit:

```markdown
## Audit Checklist

### Skills Coverage
- [ ] Does my CLAUDE.md define reusable capability modules?
- [ ] Are common GIS operations (reproject, clip, buffer, dissolve) defined as skills?
- [ ] Is there a pattern for how skills are documented and invoked?

### Instincts Coverage  
- [ ] Does my CLAUDE.md specify default CRS behavior?
- [ ] Does it define what to do when geometry is invalid?
- [ ] Does it specify behavior when a spatial join produces unexpected row counts?
- [ ] Does it say what to do when an API call fails?

### Memory Coverage
- [ ] Does my CLAUDE.md reference any session persistence?
- [ ] Is there a project state file that Claude is told to read/write?
- [ ] Are there instructions about what context to carry between sessions?

### Security Coverage
- [ ] Are there explicit guards against overwriting source data?
- [ ] Is there a confirmation requirement before dropping PostGIS tables?
- [ ] Is there protection against accidentally writing to production vs. dev environments?
- [ ] Are there file size warnings for large raster operations?

### Research-First Coverage
- [ ] Is Claude instructed to read existing code before writing new code?
- [ ] Is there a step requiring Claude to identify existing utilities before building new ones?
- [ ] Is there a proposal step before implementation?
```

---

### Step 3.4 — Deep Dive: GIS-Specific Pattern Mapping

This is where you translate the generic harness patterns into your specific GIS context.

Create the mapping file:

```bash
cat > ~/claude-audit-exercise/gis-pattern-mapping.md << 'EOF'
# GIS Pattern Mapping: everything-claude-code → GIS Workflows

## Skills → GIS Capability Modules

### Example: Reprojection Skill
```
## Skill: reproject_layer
Trigger: any request involving coordinate reference systems or projection
Steps:
  1. Identify source CRS from file metadata (not assumed)
  2. Confirm target CRS with user if not specified in task
  3. Validate geometry before reprojection
  4. Use GDAL/OGR or GeoPandas transform, never manual coordinate math
  5. Verify output CRS matches requested CRS
  6. Log: source_crs, target_crs, feature_count, geometry_validity_before/after
Output: reprojected layer + transformation log
```

### Example: Spatial Join Skill
```
## Skill: spatial_join
Trigger: any request to join datasets by location or spatial relationship
Steps:
  1. Read both datasets and report: feature counts, CRS, geometry types
  2. Confirm CRS match; reproject if needed (invoke reproject_layer skill)
  3. Identify join type (intersects, within, contains, nearest)
  4. Execute join
  5. Report: input counts, output count, unmatched features from each layer
  6. Flag if output count differs from either input by >10% (potential error)
Output: joined layer + join statistics report
```

## Instincts → GIS Decision Rules

### Geometry Validity Instinct
Trigger: Before ANY spatial operation
Default behavior (without instinct): Proceed, fail silently or produce corrupt output
Modified behavior: Run validity check, report invalid geometries, offer fix options before proceeding

### CRS Ambiguity Instinct  
Trigger: When CRS is not explicit in user request
Default behavior: Assume EPSG:4326 or use file's existing CRS silently
Modified behavior: Report detected CRS, confirm before proceeding with analysis

### Large File Instinct
Trigger: When input file > 500MB or feature count > 1,000,000
Default behavior: Attempt operation, potentially run out of memory
Modified behavior: Report size, suggest chunking strategy, confirm approach before executing

## Security → GIS Guardrails

### Source Data Protection
```
NEVER modify files in: /data/raw/, /data/source/, any directory named "original"
ALWAYS write outputs to: /data/processed/, /outputs/, or explicit user-specified path
When asked to "update" or "fix" a source file: create a copy first, modify the copy
```

### Database Safety
```
NEVER execute DROP TABLE, TRUNCATE, or DELETE without:
  1. Reporting the exact statement to be executed
  2. Reporting the row/feature count that will be affected
  3. Receiving explicit "CONFIRM" from user
ALWAYS test with SELECT before DELETE
ALWAYS use transactions for bulk PostGIS operations
```

### API Rate Limiting
```
For geocoding operations:
  - Batch requests, never individual per-row calls without batching
  - Implement exponential backoff
  - Cache results to avoid re-querying
  - Report estimated API cost before large batches
```

## Research-First → GIS Implementation Protocol

Before implementing any GIS pipeline:
1. List all input files and report: format, CRS, feature count, attribute schema
2. Identify existing scripts in the project that perform similar operations
3. Check /utils or /helpers directories for reusable functions
4. Propose the full processing chain with intermediate outputs
5. Get confirmation before executing any write operations
EOF
```

---

### Step 3.5 — Select Your 3 Adoptable Patterns

Based on your gap analysis, select the three patterns with the highest impact-to-effort ratio for your GIS workflows.

Use this decision framework:

```bash
cat > ~/claude-audit-exercise/pattern-selection.md << 'EOF'
# Pattern Selection: 3 Immediate Adoptions

## Scoring Criteria
For each candidate pattern, score 1-5:
- Impact: How much will this improve my GIS automation outcomes?
- GIS Fit: How well does this map to common GIS workflow problems?
- Adoption Effort: (inverted) How easy is it to add to my CLAUDE.md? (5 = easy)
- Risk Reduction: Does this prevent data loss or corruption?

## Candidate Patterns
(Fill in after your audit)

| Pattern | Impact | GIS Fit | Ease | Risk Red. | Total |
|---|---|---|---|---|---|
| [Pattern 1] | /5 | /5 | /5 | /5 | /20 |
| [Pattern 2] | /5 | /5 | /5 | /5 | /20 |
| [Pattern 3] | /5 | /5 | /5 | /5 | /20 |
| [Pattern 4] | /5 | /5 | /5 | /5 | /20 |
| [Pattern 5] | /5 | /5 | /5 | /5 | /20 |

## Selected Top 3
1. **[Pattern Name]** — Score: /20
   Why selected: 
   GIS application:

2. **[Pattern Name]** — Score: /20
   Why selected:
   GIS application:

3. **[Pattern Name]** — Score: /20
   Why selected:
   GIS application:
EOF
```

### Common High-Value Patterns for GIS Workflows

Based on typical GIS automation pain points, these tend to score highest:

**Pattern A: Pre-flight Data Validation Instinct**
```markdown
## Pre-flight Validation (add to CLAUDE.md)
Before executing any spatial operation on input data:
1. Run `ogrinfo -al -so {file}` or equivalent and report results
2. Check for and report: null geometries, invalid geometries, mixed geometry types
3. Confirm feature count matches user expectation
4. Do NOT proceed if validation reveals unexpected conditions — report and await instruction
```

**Pattern B: Destructive Operation Confirmation Gate**
```markdown
## Destructive Operation Gate (add to CLAUDE.md)
Operations classified as destructive:
- Writing to any existing file (overwrite)
- DELETE or DROP statements on any database object
- Removing or replacing files in /data/raw or /data/source
- Bulk attribute updates affecting >1000 features

For ALL destructive operations:
1. Print the exact operation to be performed
2. Print the scope (file path, table name, feature count affected)
3. Print "Awaiting CONFIRM to proceed."
4. Do not execute until user types "CONFIRM"
```

**Pattern C: Research-First Pipeline Design**
```markdown
## Research-First Protocol (add to CLAUDE.md)
When asked to build or modify a GIS pipeline:
1. READ: Scan all .py, .sh, .sql files in the project for existing utilities
2. INVENTORY: List what exists that could be reused or extended
3. DESIGN: Write out the proposed pipeline as pseudocode with I/O at each step
4. CONFIRM: Get user approval on the design before writing any executable code
5. IMPLEMENT: Write code one logical section at a time, testing each section
Never jump directly from request to implementation.
```

---

### Step 3.6 — Write Your Updated CLAUDE.md

Now synthesize your findings into an upgraded `CLAUDE.md`:

```bash
cat > ~/claude-audit-exercise/CLAUDE-upgraded.md << 'EOF'
# CLAUDE.md — GIS Automation Project
# Version: 2.0 (Post everything-claude-code audit)
# Last Updated: [DATE]

---

## 🗺️ Project Overview
[Your project description]

Primary GIS stack: [GeoPandas / QGIS / PostGIS / GDAL / etc.]
Primary CRS: EPSG:4326 (geographic) | EPSG:[XXXX] (projected, for analysis)
Environment: dev | staging | prod (NEVER assume prod unless explicitly stated)

---

## ⚡ Skills (Capability Modules)

### skill: validate_spatial_data
Invoked automatically before any spatial operation.
Steps:
  1. Report file format, CRS, geometry type, feature count
  2. Run geometry validity check; report count of invalid geometries
  3. Check for null geometries; report count
  4. Confirm attribute schema matches expected fields
  5. Output: validation_report.txt in working directory

### skill: reproject_layer
Invoked when: CRS transformation is needed or CRS mismatch detected.
Steps:
  1. Report source CRS (read from file, never assumed)
  2. Confirm target CRS with user if not explicit in task
  3. Invoke validate_spatial_data first
  4. Execute reprojection using [YOUR PREFERRED TOOL]
  5. Verify output CRS, report feature count preservation
Never perform reprojection in-place on source files.

### skill: spatial_join
Invoked when: joining datasets by spatial relationship.
Steps:
  1. Invoke validate_spatial_data on both inputs
  2. Report and resolve any CRS mismatches
  3. Confirm join type (intersect/within/nearest) with user
  4. Execute join
  5. Report: left_count, right_count, output_count, unmatched_count
  6. Flag if output_count differs from expected by >10%

---

## 🧠 Instincts (Decision Rules)

### instinct: crs-ambiguity
When CRS is not explicit in the user's request:
  - DO: Read CRS from input file and report it
  - DO: Ask "Detected CRS is EPSG:XXXX. Confirm this is correct?"
  - DO NOT: Assume any CRS
  - DO NOT: Silently reproject

### instinct: large-dataset
When input has >500MB file size OR >500,000 features:
  - Report: file size, feature count, estimated processing time
  - Suggest: chunking strategy or spatial index approach
  - Confirm: processing approach before executing
  - DO NOT: Attempt full-load without confirmation

### instinct: geometry-invalid
When geometry validation reveals invalid geometries:
  - Report: count and types of invalid geometries
  - Offer options: fix with buffer(0), skip invalids, abort
  - DO NOT: Proceed with invalid geometries without user decision

### instinct: unexpected-join-result
When spatial join output count is unexpected:
  - Flag immediately with counts: input_left, input_right, output
  - Suggest possible cause (one-to-many, CRS issue, predicate issue)
  - Ask for confirmation before saving output

---

## 🔒 Security Layer

### Source Data Immutability
NEVER write to or modify files in:
  - /data/raw/
  - /data/source/
  - Any directory containing "original" or "source" in path
  - Any file passed as input that has not been explicitly copied first

ALWAYS write outputs to:
  - /data/processed/
  - /outputs/
  - Or explicitly user-specified path

### Destructive Operation Gate
REQUIRED before executing any of the following:
  - File overwrite (writing to existing file path)
  - DROP TABLE, TRUNCATE, DELETE in any database
  - rm or os.remove on any file
  - Bulk UPDATE affecting the geometry column
  - Any operation on a table/file containing "prod" or "production"

Procedure:
  1. Print: "⚠️ DESTRUCTIVE OPERATION PENDING"
  2. Print: exact operation (SQL statement, file path, command)
  3. Print: scope (table name, row count, file size)
  4. Print: "Type CONFIRM to proceed or CANCEL to abort."
  5. WAIT for explicit user response

### API Safety
For any external API calls (geocoding, routing, WFS, tile services):
  - Batch requests, never row-by-row without batching
  - Cache results in /cache/ directory
  - Report estimated request count before large batches
  - Implement retry with exponential backoff
  - Never expose API keys in logs or output files

---

## 🔬 Research-First Protocol

When asked to build, modify, or debug any GIS pipeline:

**Phase 1 — READ (before writing any code)**
1. Scan project directory for existing .py, .sql, .sh files
2. List existing utilities relevant to the task
3. Read the most relevant existing file in full

**Phase 2 — DESIGN**
1. Write the proposed solution as pseudocode/outline
2. Identify each input, transformation, and output
3. Note which existing utilities will be reused

**Phase 3 — CONFIRM**
1. Present the design to the user
2. Note any assumptions made
3. Wait for approval before proceeding to implementation

**Phase 4 — IMPLEMENT**
1. Write one logical section at a time
2. Test each section before proceeding
3. Report results at each checkpoint

---

## 📁 Memory & State

### Session Context File
At the start of each session, read: .claude-context.json (if it exists)
At the end of each session, write: .claude-context.json with:
  - last_task: description of what was accomplished
  - last_output: path to most recent output file
  - open_issues: list of known problems or TODOs
  - data_state: current state of key datasets

### Project Knowledge
Key datasets and their current state:
  - [DATASET_NAME]: [path], [CRS], [last_modified], [notes]

---

## 🛠️ Commands & Environment

```bash
# Standard commands
run_tests: pytest tests/ -v
lint: ruff check . && black --check .
validate: python scripts/validate_pipeline.py
process: python pipeline.py

# GIS utilities
inspect_file: ogrinfo -al -so {file}
reproject: ogr2ogr -t_srs EPSG:{code} {output} {input}
validate_geom: python scripts/check_geometry.py {file}
```

## Environment Detection
Current environment: [dev/staging/prod]
If environment is unclear: ASK before executing any write operations.
NEVER assume production environment.

---

## 🚫 Never Do

- Never modify source/raw data files
- Never execute spatial operations on data without first running validate_spatial_data
- Never assume CRS — always read it from the file
- Never proceed with destructive operations without explicit CONFIRM
- Never write API keys to any output file, log, or comment
- Never jump from user request to code implementation without the Research-First Protocol

---

## ✅ Always Do

- Always report CRS of any spatial data you read
- Always report feature counts before and after any operation
- Always log operations with: input_path, output_path, timestamp, feature_counts
- Always create backups before any in-place modification
- Always use transactions for PostGIS batch operations
- Always confirm environment (dev/staging/prod) before write operations
EOF
```

---

### Step 3.7 — Document the Delta for Your Globe & Atlas Post

```bash
cat > ~/claude-audit-exercise/globe-atlas-post-draft.md << 'EOF'
# Draft: Globe & Atlas Tool Critic Post

**Title:** I Audited My CLAUDE.md Against a Pro Agent Harness — Here's the Delta

**Subtitle:** What the everything-claude-code repo taught me about structured AI agent design for GIS workflows

---

## The Setup

[Brief description of your existing CLAUDE.md and workflow]

I've been using Claude Code CLI for GIS automation for [timeframe]. My CLAUDE.md was [describe: minimal / moderate / detailed]. It covered [what it covered] but I suspected I was leaving performance on the table.

## The Harness I Audited Against

The **everything-claude-code** repo by affaan-m organizes Claude Code enhancements into five layers: Skills, Instincts, Persistent Memory, Security, and Research-First Patterns. Each layer solves a different failure mode in agentic workflows.

## What I Found: The Gap Analysis

### Layer 1: Skills
**Harness approach:** [describe what you found]
**My CLAUDE.md:** [describe what you had]
**Gap:** [describe the gap]
**GIS impact:** [why this matters for GIS work specifically]

### Layer 2: Instincts
**Harness approach:** [describe what you found]
**My CLAUDE.md:** [describe what you had]
**Gap:** [describe the gap]
**GIS impact:** [why this matters for GIS work specifically]

### Layer 3: Persistent Memory
**Harness approach:** [describe what you found]
**My CLAUDE.md:** [describe what you had]
**Gap:** [describe the gap]
**GIS impact:** [why this matters for GIS work specifically]

### Layer 4: Security
**Harness approach:** [describe what you found]
**My CLAUDE.md:** [describe what you had]
**Gap:** [describe the gap]
**GIS impact:** Spatial data is often irreplaceable. A guard against overwriting /data/raw/ would have saved me [specific near-miss or scenario].

### Layer 5: Research-First
**Harness approach:** [describe what you found]
**My CLAUDE.md:** [describe what you had]
**Gap:** [describe the gap]
**GIS impact:** Without this, Claude jumps to implementation and reinvents utilities that already exist in my /utils directory.

## The 3 Patterns I Adopted Immediately

### Pattern 1: [Name]
**Source:** everything-claude-code [specific section]
**Adapted for GIS as:** [your implementation]
**First test:** [how you tested it]
**Result:** [what happened]

### Pattern 2: [Name]
**Source:** everything-claude-code [specific section]
**Adapted for GIS as:** [your implementation]
**First test:** [how you tested it]
**Result:** [what happened]

### Pattern 3: [Name]
**Source:** everything-claude-code [specific section]
**Adapted for GIS as:** [your implementation]
**First test:** [how you tested it]
**Result:** [what happened]

## What the Harness Doesn't Cover (GIS-Specific Gaps)

The everything-claude-code harness is domain-agnostic. For GIS workflows, I added patterns it doesn't include:
- [Your GIS-specific addition 1]
- [Your GIS-specific addition 2]
- [Your GIS-specific addition 3]

## The Upgraded CLAUDE.md

[Link to or embed your CLAUDE-upgraded.md]

## My Rating: Tool Critic Verdict

**everything-claude-code as a reference harness for GIS work:**
- Completeness: [X]/10
- GIS applicability: [X]/10
- Adoption difficulty: [X]/10
- Documentation quality: [X]/10

**Overall:** [Your verdict and recommendation]

---

*Next audit: [what you'll review next]*
EOF
```

---

## 4. Validation

Use this checklist to confirm you've completed the exercise successfully:

### Completion Checklist

```bash
# Run this validation script
cat > ~/claude-audit-exercise/validate-completion.sh << 'EOF'
#!/bin/bash
echo "=== CLAUDE.md Audit Exercise — Completion Validation ==="
echo ""

# Check 1: Repo cloned
if [ -d ~/claude-audit-exercise/everything-claude-code ]; then
  echo "✅ everything-claude-code repo cloned"
else
  echo "❌ Repo not found — complete Step 3.1"
fi

# Check 2: Audit notes exist and have content
if [ -s ~/claude-audit-exercise/audit-notes.md ]; then
  echo "✅ Audit notes file created with content"
else
  echo "❌ Audit notes missing or empty — complete Step 3.2"
fi

# Check 3: Gap analysis completed
if [ -s ~/claude-audit-exercise/gap-analysis.md ]; then
  FILLED=$(grep -c "HIGH\|MED\|LOW" ~/claude-audit-exercise/gap-analysis.md)
  if [ "$FILLED" -gt 0 ]; then
    echo "✅ Gap analysis filled in ($FILLED severity ratings found)"
  else
    echo "⚠️  Gap analysis file exists but severity ratings not filled in"
  fi
else
  echo "❌ Gap analysis missing — complete Step 3.3"
fi

# Check 4: Pattern selection done
if [ -s ~/claude-audit-exercise/pattern-selection.md ]; then
  PATTERNS=$(grep -c "Selected" ~/claude-audit-exercise/pattern-selection.md)
  echo "✅ Pattern selection file exists"
else
  echo "❌ Pattern selection missing — complete Step 3.5"
fi

# Check 5: Upgraded CLAUDE.md created
if [ -s ~/claude-audit-exercise/CLAUDE-upgraded.md ]; then
  LINES=$(wc -l < ~/claude-audit-exercise/CLAUDE-upgraded.md)
  echo "✅ Upgraded CLAUDE.md created ($LINES lines)"
else
  echo "❌ Upgraded CLAUDE.md missing — complete Step 3.6"
fi

# Check 6: Globe & Atlas draft exists
if [ -s ~/claude-audit-exercise/globe-atlas-post-draft.md ]; then
  echo "✅ Globe & Atlas post draft created"
else