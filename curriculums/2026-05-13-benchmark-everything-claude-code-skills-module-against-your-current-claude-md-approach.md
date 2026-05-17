# Benchmark everything-claude-code Skills Module Against Your Current CLAUDE.md Approach

## A Hands-On Tutorial for Daniel

---

## 1. Introduction & Context

You've been directing Claude Code through a hand-crafted `CLAUDE.md` file — essentially a bespoke system prompt that encodes your FME workspace authoring conventions, your Globe & Atlas pipeline patterns, and your GIS domain knowledge. That approach works, but it has a cost: every new session starts cold, prompt iteration is manual, and there's no structured way to measure whether your directive is actually performing well.

**everything-claude-code (ECC)** is a meta-layer built on top of Claude Code CLI. Its core value proposition for you is threefold:

| ECC Component | What It Does | Why It Matters for You |
|---|---|---|
| **Skills** | Reusable, structured instruction modules for recurring task types | Replace repetitive CLAUDE.md boilerplate with composable units |
| **Instincts** | Persistent learned patterns extracted from past sessions | Encode FME idioms once, reuse them automatically |
| **Memory Hooks** | Save/load context across sessions | Stop re-explaining your workspace conventions every session |

This exercise has one concrete goal: **produce a single, honest data point**. You will run the same FME workspace authoring task two ways — your current `CLAUDE.md` approach and ECC's skills/instincts modules — and record the three metrics that matter: **output quality**, **iteration count**, and **token cost**. That delta is your Tool Critic data point.

---

## 2. Prerequisites

Before you start, confirm the following are in place:

### Required Tools

```bash
# Verify Claude Code CLI is installed and authenticated
claude --version
claude auth status

# Verify Node.js (ECC requires npm)
node --version   # Should be >= 18.x
npm --version

# Verify Git
git --version
```

### Required Assets You Already Have

- [ ] Your existing `CLAUDE.md` file (know its file path)
- [ ] A **specific FME workspace authoring task you've already solved manually** — this is your benchmark reference. Pick one that is:
  - Concrete and repeatable (e.g., "Author an FME workspace that reads a PostGIS layer, reprojects to WGS84, and writes to GeoJSON with attribute filtering")
  - Complex enough to reveal differences (3–5 transformers minimum)
  - Something you can evaluate quality on without running FME (schema correctness, transformer choices, parameter completeness)
- [ ] A way to track token usage — Claude Code logs this per session; note the output before each run with `claude /cost` or review session logs

### Recommended: Set Up a Comparison Workspace

```bash
# Create a clean working directory for this benchmark
mkdir ~/ecc-benchmark
cd ~/ecc-benchmark

# Record your baseline task description in a plain text file
cat > task.txt << 'EOF'
[PASTE YOUR FME WORKSPACE AUTHORING TASK HERE — be precise]
Example: "Author an FME 2024 workspace that reads a GeoPackage containing 
polygon features, calculates area in hectares using AreaCalculator, 
filters features where area > 5ha, and writes output to a PostGIS table 
named 'large_parcels' with a spatial index."
EOF
```

---

## 3. Step-by-Step Guide

### Phase A — Baseline: Record Your Current CLAUDE.md Performance

You need a clean baseline before touching ECC. Do this first.

#### Step A1 — Run Your Benchmark Task with Your Current Setup

```bash
# Navigate to a clean project directory (no ECC installed yet)
mkdir ~/ecc-benchmark/baseline-run
cd ~/ecc-benchmark/baseline-run

# Copy your existing CLAUDE.md into this directory
cp /path/to/your/CLAUDE.md .

# Note the exact time and open a new Claude Code session
# This ensures a cold start — no cached context
claude
```

Inside the Claude Code session, paste your benchmark task verbatim from `task.txt`. Do **not** refine or clarify mid-session. Let it run.

#### Step A2 — Record Baseline Metrics

After the session completes, immediately record the following. Create a metrics file:

```bash
cat > ~/ecc-benchmark/baseline-metrics.md << 'EOF'
# Baseline Metrics — CLAUDE.md Approach
Date: [TODAY]
Task: [ONE-LINE DESCRIPTION]

## Iteration Count
- Number of back-and-forth exchanges before acceptable output: ___
- Number of corrections you had to make: ___

## Token Cost
- Input tokens: ___
- Output tokens: ___
- Total cost (USD): ___
(Find these in Claude Code session output or ~/.claude/logs/)

## Output Quality Score (0-10 scale)
Rate each dimension yourself:
- Correct transformer selection: ___/10
- Parameter completeness: ___/10
- FME best-practice adherence: ___/10
- Output schema correctness: ___/10
- Overall: ___/10

## Raw Output
[Paste or link the generated workspace description/script here]

## Notes
- Where did it struggle?
- What did you have to correct?
- What was missing from the output?
EOF
```

> **Be honest here.** The baseline is only useful if it reflects reality. If you had to fix three transformer parameters, write that down.

---

### Phase B — Install and Explore everything-claude-code

#### Step B1 — Clone the Repository

```bash
cd ~/ecc-benchmark
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
```

#### Step B2 — Review the Repository Structure

Before installing anything, orient yourself:

```bash
# Get a high-level view of what you're working with
ls -la

# The source material confirms these key areas exist:
# - Skills modules (208 skills per the catalog)
# - Agents (55 agents)
# - Legacy command shims (72 shims)
# - Hooks for memory persistence
# Look for these directories:
find . -maxdepth 2 -type d | sort
```

> **Note:** The source material confirms ECC contains 55 agents, 208 skills, and 72 legacy command shims as of v2.0.0-rc.1. The exact directory layout within the repo should be explored directly from your clone — the source content does not enumerate every subdirectory, so map it yourself here.

#### Step B3 — Install via npm (Universal Package)

The source material confirms two npm packages: `ecc-universal` and `ecc-agentshield`. For this benchmark, use `ecc-universal`:

```bash
# Install the universal package globally
npm install -g ecc-universal

# Verify installation
ecc-universal --version 2>/dev/null || echo "Check npm bin path"

# Alternative: use the repo directly if npm install has issues
# The repo is your ground truth — work from the clone
cd ~/ecc-benchmark/everything-claude-code
npm install
```

> **Transparency checkpoint:** The source content does not provide the exact CLI syntax for `ecc-universal` beyond the npm package name. After installation, run `ecc-universal --help` to see available commands. If the package exposes no direct CLI, the skills are likely consumed as files you reference — explore the installed package contents.

#### Step B4 — Read the Shorthand Guide First

The source material explicitly states: *"Read this first."* The guides are linked from X (formerly Twitter) — the shorthand guide is at:

```
https://x.com/affaanmustafa/status/2012378465664745795
```

Spend 15 minutes reading it before proceeding. Key concepts to note for this benchmark:

- How skills are structured and invoked
- How instincts differ from skills
- How memory hooks work across sessions
- The research-first development pattern

#### Step B5 — Explore the Skills Catalog

```bash
cd ~/ecc-benchmark/everything-claude-code

# Find skills-related files
find . -name "*.md" | xargs grep -l -i "skill" 2>/dev/null | head -20

# Find instinct-related files  
find . -name "*.md" | xargs grep -l -i "instinct" 2>/dev/null | head -20

# Look for any GIS, data pipeline, or ETL adjacent skills
# that might be relevant to FME workspace authoring
grep -r -i "gis\|geospatial\|etl\|pipeline\|transform" . \
  --include="*.md" -l 2>/dev/null

grep -r -i "gis\|geospatial\|etl\|pipeline\|transform" . \
  --include="*.json" -l 2>/dev/null
```

> **What you're looking for:** Any skills that map to: data pipeline authoring, ETL task specification, API/schema-first development, or research-first patterns. None may directly mention FME — that's fine. The question is which skills' *structure* is transferable to your FME workspace authoring task.

#### Step B6 — Identify the Most Relevant Skills for Your Task

Based on your exploration, select 2–3 skills or instinct modules to apply. Document your selection:

```bash
cat > ~/ecc-benchmark/ecc-skill-selection.md << 'EOF'
# ECC Skills Selected for FME Benchmark

## Skills Chosen
1. [Skill name] — Reason: ___
2. [Skill name] — Reason: ___
3. [Instinct module name] — Reason: ___

## Skills Reviewed but Not Selected
- [Skill name] — Why skipped: ___

## Gap Assessment
Skills I expected to exist but didn't find:
- ___
EOF
```

---

### Phase C — Run the ECC-Augmented Benchmark

#### Step C1 — Set Up the ECC-Augmented Project

```bash
mkdir ~/ecc-benchmark/ecc-run
cd ~/ecc-benchmark/ecc-run

# Copy your task definition
cp ~/ecc-benchmark/task.txt .

# Do NOT copy your existing CLAUDE.md — you're testing ECC's approach
# Instead, you will construct a CLAUDE.md (or equivalent) 
# using ECC's skills modules as the directive source
```

#### Step C2 — Construct an ECC-Based Directive

The ECC system extends Claude Code at the `CLAUDE.md` layer. Based on the skills you selected in Step B6, compose a new directive that uses ECC's structured format rather than your hand-written one:

```bash
# Create a new CLAUDE.md that references ECC skills
cat > ~/ecc-benchmark/ecc-run/CLAUDE.md << 'EOF'
# ECC-Augmented Directive for FME Workspace Authoring Benchmark

## Active Skills
[Reference the ECC skills you selected in Step B6 here.
Copy the actual skill content or reference path from the ECC repo.]

## Active Instincts
[Reference any instinct modules from ECC here.]

## Task Context
Domain: FME workspace authoring, GIS data pipelines
Platform: FME 2024
Output format: [your preferred format — JSON workspace spec, pseudocode, etc.]

## NOTE FOR BENCHMARK INTEGRITY
This CLAUDE.md was constructed using ECC skills modules ONLY.
No content was carried over from the baseline CLAUDE.md.
EOF
```

> **Critical for benchmark integrity:** The point is to test what ECC's skills give you *without* your existing CLAUDE.md knowledge. If you paste your entire CLAUDE.md into this file and just add ECC skills on top, you're not measuring ECC — you're measuring ECC + your existing work. Keep them separate.

#### Step C3 — Run the Benchmark Task with ECC

```bash
cd ~/ecc-benchmark/ecc-run

# Open a fresh Claude Code session — cold start, same as baseline
claude
```

Paste the **exact same task text** from `task.txt`. Same task, same wording. This is non-negotiable for a valid comparison.

#### Step C4 — Record ECC Metrics

```bash
cat > ~/ecc-benchmark/ecc-metrics.md << 'EOF'
# ECC Metrics — Skills/Instincts Approach
Date: [TODAY — same day as baseline ideally]
Task: [SAME ONE-LINE DESCRIPTION AS BASELINE]
ECC Version: v2.0.0-rc.1 (or check your clone's git tag)
Skills Used: [list them]

## Iteration Count
- Number of back-and-forth exchanges before acceptable output: ___
- Number of corrections you had to make: ___

## Token Cost
- Input tokens: ___
- Output tokens: ___
- Total cost (USD): ___

## Output Quality Score (0-10 scale — SAME RUBRIC AS BASELINE)
- Correct transformer selection: ___/10
- Parameter completeness: ___/10
- FME best-practice adherence: ___/10
- Output schema correctness: ___/10
- Overall: ___/10

## Raw Output
[Paste or link the generated workspace description/script here]

## Notes
- Where did it struggle?
- What did you have to correct?
- What did ECC add that baseline missed?
- What did baseline have that ECC missed?
EOF
```

---

### Phase D — Analysis and Tool Critic Data Point

#### Step D1 — Generate the Delta Report

```bash
cat > ~/ecc-benchmark/delta-report.md << 'EOF'
# Tool Critic Data Point — ECC vs CLAUDE.md Benchmark
Date: ___
Task: ___

## The Delta

| Metric | Baseline (CLAUDE.md) | ECC Skills/Instincts | Delta | Winner |
|--------|---------------------|----------------------|-------|--------|
| Iteration count | ___ | ___ | ___ | ___ |
| Input tokens | ___ | ___ | ___ | ___ |
| Output tokens | ___ | ___ | ___ | ___ |
| Total cost (USD) | ___ | ___ | ___ | ___ |
| Quality: Transformer selection | ___/10 | ___/10 | ___ | ___ |
| Quality: Parameter completeness | ___/10 | ___/10 | ___ | ___ |
| Quality: FME best practices | ___/10 | ___/10 | ___ | ___ |
| Quality: Schema correctness | ___/10 | ___/10 | ___ | ___ |
| **Quality: OVERALL** | **___/10** | **___/10** | **___** | **___** |

## Qualitative Observations

### What ECC Skills Added
-
-
-

### What Your CLAUDE.md Has That ECC Didn't Cover
-
-
-

### Failure Modes
- ECC failures: ___
- CLAUDE.md failures: ___

## Verdict

### Should you adopt ECC for FME workspace authoring?
[ ] Yes — fully replace CLAUDE.md
[ ] Partial — use ECC skills + port your CLAUDE.md knowledge into ECC format
[ ] No — CLAUDE.md performs better for this specific domain
[ ] Hybrid — use ECC memory/hooks layer but keep CLAUDE.md skill content

### Estimated ROI for Globe & Atlas Pipeline
If ECC reduces iteration count by ___%, and you run ___ FME authoring sessions/week,
that's approximately ___ minutes saved per week.

At Claude Code token costs, the token delta is $___ per session.

## Action Item
[ONE CONCRETE NEXT STEP based on what you found]
EOF
```

#### Step D2 — Honest Self-Assessment Questions

Answer these in your delta report:

1. **Did ECC's skills structure force you to think more clearly about the task before running it?** (Research-first pattern benefit)
2. **Did ECC's output require less domain correction than your CLAUDE.md output?** This reveals whether your CLAUDE.md is over-fitted to your mental model vs. whether ECC's general patterns transfer better.
3. **Was the token cost higher for ECC?** More structured prompts are often longer — the question is whether the quality-per-token ratio is better.
4. **Which approach would be easier to hand to a colleague?** This reveals maintainability, which matters as your Globe & Atlas team grows.

---

## 4. Validation

You've completed this exercise successfully when all of the following are true:

### Checklist

```
[ ] CLONE COMPLETE
    - everything-claude-code repo cloned to ~/ecc-benchmark/everything-claude-code
    - npm install completed without fatal errors
    - You can locate the skills directory in the repo

[ ] BASELINE RECORDED
    - baseline-metrics.md exists and is filled in completely
    - Raw output from baseline session is saved
    - Token costs are recorded (not estimated)

[ ] ECC RUN COMPLETE
    - ecc-metrics.md exists and is filled in completely
    - You used the SAME task text for both runs
    - ECC-run CLAUDE.md was constructed from ECC skills, NOT copied from baseline
    - Raw output from ECC session is saved

[ ] DELTA REPORT COMPLETE
    - delta-report.md exists with all table cells filled
    - You have a written verdict (even if "inconclusive — need more data")
    - You have ONE concrete action item

[ ] TOOL CRITIC DATA POINT CAPTURED
    - The delta report is committed or saved somewhere you'll find it
    - You can articulate the finding in one sentence:
      "ECC skills [improved / degraded / had no effect on] FME workspace 
       authoring quality by [X] while [increasing / decreasing / not changing] 
       token cost by [Y%] and [reducing / increasing] iteration count by [Z]."
```

### Quality Gate for the Output Comparison

The output comparison is only valid if:

- Both runs used identical task text (verify with `diff baseline-run/task.txt ecc-run/task.txt`)
- Both sessions were cold-start (no prior context carryover)
- You used the same quality rubric for both (same 4 dimensions, same 0–10 scale)
- You scored both outputs *before* writing the delta (avoid anchoring bias)

---

## 5. Next Steps

Based on what your delta reveals, three paths forward:

### Path A: ECC Wins on Quality or Token Efficiency

If ECC's skills/instincts produced better FME output or lower token cost:

1. **Port your CLAUDE.md knowledge into ECC skill format** — Structure your FME conventions as composable ECC skills rather than a monolithic directive. The source material confirms 208 skills exist as reference patterns.
2. **Activate ECC's memory hooks** for your Globe & Atlas sessions — persistent context across sessions means you stop re-explaining your PostGIS schema, your FME version, and your coordinate reference system conventions every cold start.
3. **Explore the Hermes operator story** — the source material points to `docs/HERMES-SETUP.md` for the operator workflow, which may map to your pipeline orchestration needs.

```bash
# Start the Hermes setup if Path A applies
cat ~/ecc-benchmark/everything-claude-code/docs/HERMES-SETUP.md
```

### Path B: Your CLAUDE.md Wins

If your existing approach outperforms ECC for FME workspace authoring:

1. **Document why** — your CLAUDE.md likely contains FME-specific domain knowledge that ECC's general skills don't have. That's a feature, not a failure.
2. **Selectively adopt ECC's infrastructure** without replacing your content — memory hooks and session persistence are valuable regardless of skill quality.
3. **Contribute back** — if you've built strong FME/GIS skills in your CLAUDE.md, they're candidates for ECC contributions. The repo has 170+ contributors.

### Path C: Results Are Mixed or Inconclusive

1. **Run a second benchmark with a different FME task** — one data point is not enough. Pick a task from a different part of your workflow (e.g., coordinate transformation instead of attribute filtering).
2. **Test the continuous learning loop** — the source material describes auto-extraction of patterns from sessions into reusable skills. Run 3–5 ECC sessions on related FME tasks and see if the instincts improve.
3. **Review the Longform Guide** for token optimization and memory persistence techniques before concluding:
   ```
   https://x.com/affaanmustafa/status/2014040193557471352
   ```

### Ongoing: Feed This Into Your Tool Critic Practice

The structured delta report you created here is the template. Apply it to every tool evaluation:

```bash
# Save the template for future benchmarks
cp ~/ecc-benchmark/delta-report.md ~/ecc-benchmark/TOOL-CRITIC-TEMPLATE.md

# Clear the values, keep the structure
# Use it for: MCP server evaluations, new FME transformer AI suggestions,
# Globe & Atlas pipeline tooling decisions
```

---

## Appendix: Quick Reference

### Key Files Created in This Exercise

```
~/ecc-benchmark/
├── task.txt                      # Your benchmark task (shared by both runs)
├── baseline-metrics.md           # CLAUDE.md approach results
├── ecc-metrics.md               # ECC approach results
├── delta-report.md              # Your Tool Critic data point
├── ecc-skill-selection.md       # Which ECC skills you chose and why
├── TOOL-CRITIC-TEMPLATE.md      # Reusable template for future evals
├── baseline-run/
│   └── CLAUDE.md                # Your existing directive
└── ecc-run/
    └── CLAUDE.md                # ECC-constructed directive
```

### ECC npm Packages (from source)

| Package | Purpose |
|---|---|
| `ecc-universal` | Main installation — skills, agents, shims |
| `ecc-agentshield` | Security scanning layer |

### Token Tracking in Claude Code

```bash
# During a session, check accumulated cost:
/cost

# After a session, check logs:
ls ~/.claude/logs/ 2>/dev/null || ls ~/.config/claude/logs/ 2>/dev/null
```

> **One final note on honesty:** The source material for ECC is extensive but the tutorial above is explicit where the source content does not provide specific CLI syntax (e.g., exact `ecc-universal` subcommands, exact skills directory names). In those gaps, you're instructed to explore the actual clone rather than trust invented details. That exploration *is* part of the exercise — your first-hand findings are more valuable than any pre-written command that might be stale.