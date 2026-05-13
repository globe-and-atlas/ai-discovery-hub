# Benchmark everything-claude-code Skills Module Against Your Current CLAUDE.md Approach

## A Practical Curriculum for FME Workspace Authors Using Claude Code CLI

---

## 1. Introduction & Context

### What This Is

[everything-claude-code](https://github.com/affaan-m/everything-claude-code) is a meta-layer harness built on top of the Claude Code CLI. It extends your existing workflow with:

- **Skills modules** — reusable, structured capability definitions that guide Claude toward expert-level behaviour in specific domains
- **Instincts modules** — heuristic patterns that shape how Claude approaches problems before writing a single line of code
- **Persistent memory** — context that survives across sessions, reducing repetitive prompt bootstrapping
- **Research-first patterns** — forcing Claude to investigate before acting, reducing hallucinated solutions
- **Security layers** — guardrails to prevent destructive operations in automated pipelines

### Why It Matters for Your Workflow

You already use a `CLAUDE.md` directive file to orient Claude Code for FME workspace authoring tasks — things like building transformers, writing Python callouts, structuring workspace templates for Globe & Atlas pipelines. That approach works, but it has costs:

| Pain Point | Current CLAUDE.md Approach | everything-claude-code Potential |
|---|---|---|
| Repetitive context-setting | Re-stated every session | Persisted in memory modules |
| Domain skills (FME, Python, CRS) | Embedded in monolithic CLAUDE.md | Modular, composable skills |
| Iteration count | Varies per task | Potentially reduced via instincts |
| Token cost | Baseline | Measurable delta |

This exercise gives you a **concrete, evidence-based data point**: does the skills/instincts approach actually outperform your current CLAUDE.md directive on a real FME task you've already solved?

---

## 2. Prerequisites

Before starting, confirm you have the following.

### Hard Requirements

- [ ] **Claude Code CLI installed and authenticated**
  ```bash
  claude --version
  # Expected: claude-code 1.x.x or higher
  ```
- [ ] **Git installed**
  ```bash
  git --version
  ```
- [ ] **Node.js ≥ 18** (required by Claude Code CLI internals)
  ```bash
  node --version
  ```
- [ ] **An existing CLAUDE.md file** you currently use for FME workspace authoring — this is your control baseline
- [ ] **A solved FME workspace authoring task** you completed manually or with your CLAUDE.md approach. You need:
  - The original task description/prompt you used
  - The final output (`.fmw` file, Python script, or transformer config)
  - A rough note of how many prompt iterations it took
- [ ] **A cost-tracking baseline** — either from Claude Code's built-in usage display or your Anthropic console

### Helpful but Not Required

- [ ] Familiarity with YAML or JSON (skills files use structured config)
- [ ] Basic understanding of what `CLAUDE.md` does in Claude Code (it's injected as system context at session start)

### Reference: Your Benchmark Task

Pick a task you've **already solved** that meets these criteria:

```
Good benchmark tasks:
  ✓ Takes 3–10 prompt iterations to solve cleanly
  ✓ Involves FME-specific knowledge (transformer chains, coordinate systems, reader/writer params)
  ✓ Has a clear, verifiable output (the workspace runs, produces correct output)
  ✓ Is representative of Globe & Atlas pipeline work

Avoid for this benchmark:
  ✗ Trivial one-shot tasks (too little signal)
  ✗ Tasks requiring live data connections you can't reproduce
  ✗ Tasks so complex they take 30+ iterations (too much noise)
```

**Document your baseline now, before cloning anything:**

```markdown
## My Benchmark Task Record

### Task Description (the prompt I used)
[Paste your original prompt here]

### Output Produced
[File path or description of the .fmw / script produced]

### Iteration Count (baseline)
[Number of back-and-forth prompts to reach acceptable output]

### Token Cost (baseline)
[Approximate from Claude console, or "not tracked"]

### Subjective Quality Score (1–5)
[How satisfied were you with the output?]
```

---

## 3. Step-by-Step Guide

### Phase 1: Clone and Explore the Repository

#### Step 1.1 — Clone everything-claude-code

```bash
# Navigate to your projects directory
cd ~/projects

# Clone the repo
git clone https://github.com/affaan-m/everything-claude-code.git

# Enter it
cd everything-claude-code

# List the top-level structure
ls -la
```

You should see a structure similar to:

```
everything-claude-code/
├── CLAUDE.md               ← The repo's own Claude directive (study this!)
├── skills/                 ← Skills module definitions
├── instincts/              ← Instincts/heuristic patterns
├── memory/                 ← Persistent memory templates
├── security/               ← Guardrail configurations
├── examples/               ← Usage examples
└── README.md
```

#### Step 1.2 — Read the Repository's Own CLAUDE.md

This is the most instructive file in the repo. Before touching anything else:

```bash
cat CLAUDE.md
```

**As you read, annotate mentally:**
- How is it structured differently from yours?
- Does it reference skills/instincts files, or does it contain everything inline?
- What patterns does it use that your CLAUDE.md doesn't?

#### Step 1.3 — Inventory the Skills Directory

```bash
# List all skills files
find skills/ -type f | sort

# Read each one — they're usually short
cat skills/*.md   # or skills/*.yaml depending on the repo structure
```

**Look for:**
- How skills are named and scoped
- Whether skills have input/output contracts
- How domain-specific knowledge is encoded (this is what you'll adapt for FME)

#### Step 1.4 — Inventory the Instincts Directory

```bash
find instincts/ -type f | sort
cat instincts/*
```

Instincts are typically short heuristic rules like:
- "Always read existing code before modifying it"
- "Prefer reversible operations"
- "Ask for clarification when requirements have two valid interpretations"

Note which instincts would be **high-value for FME workspace authoring specifically**.

---

### Phase 2: Create an FME-Specific Skills Module

This is where you translate your domain knowledge into the everything-claude-code format.

#### Step 2.1 — Create a Working Directory

```bash
# Create a local workspace for this experiment
mkdir ~/projects/fme-claude-benchmark
cd ~/projects/fme-claude-benchmark

# Create subdirectories mirroring the everything-claude-code structure
mkdir -p skills instincts memory
```

#### Step 2.2 — Write an FME Workspace Authoring Skill

Create `skills/fme-workspace-authoring.md`:

```bash
cat > skills/fme-workspace-authoring.md << 'EOF'
# Skill: FME Workspace Authoring

## Domain
Safe Software FME (Feature Manipulation Engine) workspace design and implementation.

## Capability Scope
- Design transformer chains for spatial and tabular data transformation
- Write Python callout scripts compatible with FME's scripting environment
- Configure Reader and Writer parameters for common formats (GeoJSON, Shapefile, PostGIS, WFS, CSV)
- Apply coordinate reference system (CRS) transformations using appropriate FME transformers
- Structure workspaces for the Globe & Atlas pipeline conventions

## Activation Trigger
Activate this skill when the user's request mentions: FME, workspace, transformer, .fmw, 
FeatureReader, FeatureWriter, FMEObjects, Python callout, CRS reprojection, 
Safe Software, Globe & Atlas pipeline.

## Research-First Protocol
Before proposing any transformer chain:
1. Confirm the input data format and schema
2. Confirm the target output format and schema
3. Identify the CRS of input and whether reprojection is needed
4. Ask: "Does an existing transformer handle this, or is a custom Python callout needed?"

## Output Contract
All FME workspace descriptions must include:
- Transformer list in order (Reader → [chain] → Writer)
- For each transformer: name, key parameters, purpose in one sentence
- Any Python callout scripts in full, with inline comments
- Explicit CRS handling steps if projection change is involved
- Known failure modes and how the workspace handles them

## Quality Gates
- [ ] Workspace handles null/missing geometry gracefully
- [ ] All attribute names follow the target schema exactly (case-sensitive)
- [ ] CRS is explicitly set at the Writer, not assumed
- [ ] Python callouts include try/except blocks
- [ ] Large dataset considerations noted (chunking, streaming if applicable)

## Globe & Atlas Specific Conventions
- Output CRS: EPSG:4326 unless otherwise specified
- Attribute naming: snake_case
- Null geometry: log and pass-through, do not discard
- Workspace naming: [source]_to_[target]_[version].fmw

## Anti-Patterns (Never Do)
- Do not use deprecated FME transformers (check FME version compatibility)
- Do not hardcode file paths — use Published Parameters
- Do not assume input CRS — always read it from the data or ask
- Do not leave Python callouts without error handling
EOF
```

#### Step 2.3 — Write an FME-Specific Instincts File

Create `instincts/fme-instincts.md`:

```bash
cat > instincts/fme-instincts.md << 'EOF'
# Instincts: FME Workspace Authoring

These are fast heuristics applied before deep reasoning begins.

## Instinct 1: Schema First
Before designing any transformer chain, ask for or infer the input and output schema.
A workspace designed against the wrong schema wastes all subsequent effort.

## Instinct 2: Transformer Exists, Probably
FME has 500+ transformers. Before suggesting a Python callout, check whether a 
native transformer handles the transformation. Python callouts are maintenance debt.

## Instinct 3: CRS Is Never Obvious
Never assume the input CRS matches the output CRS. Always make CRS handling explicit,
even if it's a no-op (add a CoordinateSystemSetter with "as-is" to document intent).

## Instinct 4: Published Parameters Over Hardcoding
Any file path, database connection, or environment-specific value must be a 
Published Parameter. This is the difference between a reusable workspace and a 
one-time script.

## Instinct 5: Test With Small Data First
When proposing a workspace design, always note which transformer is the best 
"sample point" to run a partial test before full execution.

## Instinct 6: Reversibility
Prefer non-destructive workspace designs. Write to new output rather than 
overwriting source. Flag any operation that modifies source data.
EOF
```

#### Step 2.4 — Create a Memory Seed File

This simulates the persistent memory feature — context that Claude loads at session start:

```bash
cat > memory/fme-project-context.md << 'EOF'
# Project Memory: Globe & Atlas FME Pipeline

## Project Overview
Building FME workspaces for the Globe & Atlas data pipeline. Primary role:
transform heterogeneous geospatial source data into standardised GeoJSON/PostGIS
outputs for the Atlas web application.

## Active Pipeline Components
- Source formats in use: Shapefile, WFS, GeoJSON, CSV with WKT geometry, PostGIS
- Target format: PostGIS (primary), GeoJSON (secondary/export)
- Standard output CRS: EPSG:4326
- FME version: [YOUR VERSION HERE]

## Conventions Established
- snake_case attribute names
- Null geometry: log to feature_log table, continue processing
- Published Parameters required for all connection strings
- Workspace versioning in filename: v1, v2, etc.

## Recently Solved Patterns
[You will populate this as you work — add successful transformer patterns here]

## Known Problem Areas
[Add tricky edge cases you've encountered]
EOF
```

---

### Phase 3: Set Up the Benchmark Experiment

Now you'll run your task twice — once with your original CLAUDE.md approach, once with the everything-claude-code skills/instincts approach — and measure the difference.

#### Step 3.1 — Prepare the Control Run Environment

```bash
# Create a directory for the control (baseline) run
mkdir -p ~/projects/fme-claude-benchmark/runs/control
cd ~/projects/fme-claude-benchmark/runs/control

# Copy your existing CLAUDE.md here
cp ~/path/to/your/existing/CLAUDE.md ./CLAUDE.md

# Verify it's there
cat CLAUDE.md
```

#### Step 3.2 — Prepare the Treatment Run Environment

```bash
# Create a directory for the treatment (skills/instincts) run
mkdir -p ~/projects/fme-claude-benchmark/runs/treatment
cd ~/projects/fme-claude-benchmark/runs/treatment

# Create a new CLAUDE.md that loads the skills and instincts modules
cat > CLAUDE.md << 'EOF'
# Claude Code Directive: FME Workspace Authoring (Skills/Instincts Mode)

## Active Modules
The following skill and instinct files govern your behaviour in this session.
Read and apply all of them before responding to any task.

@../../skills/fme-workspace-authoring.md
@../../instincts/fme-instincts.md
@../../memory/fme-project-context.md

## Session Behaviour
- Apply the Research-First Protocol from the FME skill before proposing solutions
- Check all Quality Gates before presenting a final workspace design
- Follow Globe & Atlas conventions without being asked
- State which instincts you applied at the end of each major response

## Meta-Instruction
If asked to do something that conflicts with the anti-patterns list in the FME skill,
note the conflict and propose a compliant alternative.
EOF
```

> **Note on `@file` syntax:** Claude Code supports file inclusion via `@path/to/file` in CLAUDE.md. If your version doesn't support this, inline the content directly — the structure still applies, it's just less modular.

#### Step 3.3 — Create Your Measurement Scorecard

```bash
cat > ~/projects/fme-claude-benchmark/scorecard.md << 'EOF'
# Benchmark Scorecard: CLAUDE.md vs Skills/Instincts

## Task Description
[Paste your benchmark task description here]

---

## Run 1: Control (Existing CLAUDE.md)

### Setup
- CLAUDE.md approach: [describe your current approach briefly]
- Session start time: 
- Session end time:

### Metrics
| Metric | Value |
|---|---|
| Iteration count (prompts to acceptable output) | |
| Approximate token usage (input) | |
| Approximate token usage (output) | |
| Estimated cost (USD) | |

### Output Quality Assessment
| Criterion | Score (1–5) | Notes |
|---|---|---|
| Correctness (workspace would run) | | |
| Completeness (all requirements met) | | |
| FME conventions followed | | |
| Globe & Atlas conventions followed | | |
| Code quality (Python callouts if any) | | |
| How much manual editing needed after? | | |

### Qualitative Notes
[What did Claude get right first try? What needed correction?]

---

## Run 2: Treatment (Skills/Instincts Modules)

### Setup  
- Skills loaded: fme-workspace-authoring.md, fme-instincts.md, fme-project-context.md
- Session start time:
- Session end time:

### Metrics
| Metric | Value |
|---|---|
| Iteration count (prompts to acceptable output) | |
| Approximate token usage (input) | |
| Approximate token usage (output) | |
| Estimated cost (USD) | |

### Output Quality Assessment
| Criterion | Score (1–5) | Notes |
|---|---|---|
| Correctness (workspace would run) | | |
| Completeness (all requirements met) | | |
| FME conventions followed | | |
| Globe & Atlas conventions followed | | |
| Code quality (Python callouts if any) | | |
| How much manual editing needed after? | | |

### Qualitative Notes
[What did Claude get right first try? What needed correction?]
[Did it explicitly invoke the Research-First Protocol?]
[Did it check Quality Gates unprompted?]

---

## Delta Analysis

| Metric | Control | Treatment | Delta | Verdict |
|---|---|---|---|---|
| Iterations | | | | |
| Token cost | | | | |
| Quality score (avg) | | | | |
| Time to acceptable output | | | | |

## Key Finding
[One paragraph: what does this data point tell you about whether skills/instincts
modules improve your FME workflow enough to justify the setup overhead?]

## Decision
- [ ] Adopt skills/instincts approach wholesale
- [ ] Hybrid: keep CLAUDE.md but add specific skills modules for complex tasks
- [ ] No change: existing CLAUDE.md is sufficient
- [ ] Need more data points before deciding
EOF
```

---

### Phase 4: Execute the Control Run

#### Step 4.1 — Start a Fresh Claude Code Session (Control)

```bash
cd ~/projects/fme-claude-benchmark/runs/control

# Start Claude Code — it will auto-load CLAUDE.md from the current directory
claude
```

#### Step 4.2 — Run Your Benchmark Task

Use the **exact same prompt** you used when you originally solved the task. Do not add extra context. The goal is to reproduce the original conditions.

```
# Example structure of what to paste:
"I need an FME workspace that [your original task description]. 
The input is [format/source]. The output should be [format/target]."
```

#### Step 4.3 — Track Iterations Carefully

Keep a tally in a scratch file as you work:

```bash
# In a separate terminal
cat > ~/projects/fme-claude-benchmark/control-log.md << 'EOF'
# Control Run — Iteration Log

## Iteration 1
Prompt: [what you sent]
Response quality: [good/partial/wrong]
Correction needed: [yes/no — describe]

## Iteration 2
...
EOF
```

#### Step 4.4 — Record Final Metrics

When you reach an acceptable output:

1. Check your Claude console (console.anthropic.com) or the session's token display for usage
2. Count total iterations
3. Save the final output to `runs/control/output/`
4. Fill in the Control section of `scorecard.md`

---

### Phase 5: Execute the Treatment Run

#### Step 5.1 — Start a Fresh Claude Code Session (Treatment)

> **Critical:** Use a completely fresh session. Do not continue from the control session — you want no memory carryover.

```bash
cd ~/projects/fme-claude-benchmark/runs/treatment

# New session — loads the skills/instincts CLAUDE.md
claude
```

#### Step 5.2 — Verify Skills Were Loaded

Before running your task, ask Claude to confirm its loaded context:

```
What skills and instincts are you operating with in this session? 
List the key constraints and protocols you'll apply to FME workspace tasks.
```

A good response will demonstrate it has absorbed:
- The Research-First Protocol
- The Output Contract (transformer list format, etc.)
- The Quality Gates
- The Anti-Patterns

If the response is vague or generic, check your `@file` includes are working — you may need to inline the content.

#### Step 5.3 — Run the Exact Same Benchmark Task

Use the **identical prompt** as the control run. Resist the temptation to rephrase it — you're testing the harness, not the prompt quality.

#### Step 5.4 — Observe Behavioural Differences

Watch for:

```
Positive signals (skills/instincts working):
  ✓ Claude asks about input schema before proposing a solution
  ✓ Claude explicitly checks for native transformers before suggesting Python
  ✓ Output format matches the Output Contract (transformer list, then config, then code)
  ✓ CRS handling is explicit and unprompted
  ✓ Published Parameters are used without being asked
  ✓ Claude mentions which Quality Gates it checked

Negative signals (skills/instincts not working):
  ✗ Response identical to control — skills not being applied
  ✗ More iterations needed because Research-First Protocol creates friction
  ✗ Quality Gates flagged issues that required extra rounds of correction
```

#### Step 5.5 — Record Final Metrics

Repeat the same logging process as the control run. Fill in the Treatment section of `scorecard.md`.

---

### Phase 6: Analyse the Delta

#### Step 6.1 — Complete the Scorecard

```bash
# Open and complete your scorecard
open ~/projects/fme-claude-benchmark/scorecard.md
# or: code scorecard.md / vim scorecard.md
```

#### Step 6.2 — Calculate the Deltas

Use this calculation template:

```
Iteration Delta = Control_Iterations - Treatment_Iterations
  Positive = skills/instincts reduced iterations ✓
  Negative = skills/instincts added friction ✗
  Zero = no difference

Cost Delta = Control_Cost - Treatment_Cost
  Note: Treatment may have HIGHER input token cost (larger CLAUDE.md context)
  but LOWER total cost if fewer iterations are needed.
  Calculate: net_cost_delta = (control_total) - (treatment_total)

Quality Delta = Treatment_AvgScore - Control_AvgScore
  Positive = skills/instincts improved output quality ✓
```

#### Step 6.3 — Interpret Your Results

Use this decision matrix:

```
┌─────────────────────────────────┬───────────────────────────────────┐
│ Result Pattern                  │ Interpretation                    │
├─────────────────────────────────┼───────────────────────────────────┤
│ Fewer iterations + lower cost   │ Strong adopt signal               │
│ + higher quality                │                                   │
├─────────────────────────────────┼───────────────────────────────────┤
│ Fewer iterations + higher cost  │ Quality/speed trade-off —        │
│ + higher quality                │ worth it for complex tasks        │
├─────────────────────────────────┼───────────────────────────────────┤
│ Same iterations + higher cost   │ Skills overhead not justified     │
│ + same quality                  │ for this task type                │
├─────────────────────────────────┼───────────────────────────────────┤
│ More iterations + any cost      │ Skills files need refinement      │
│                                 │ or task is too simple to benefit  │
├─────────────────────────────────┼───────────────────────────────────┤
│ Fewer iterations + lower cost   │ Skills modularise value but       │
│ + same quality                  │ quality ceiling is already met    │
└─────────────────────────────────┴───────────────────────────────────┘
```

---

## 4. Validation

### How to Know You Completed This Successfully

Work through this checklist. Every item should be checkable.

#### Setup Validation
- [ ] `everything-claude-code` repo cloned and explored
- [ ] You can articulate the difference between a **skill** and an **instinct** in this system
- [ ] You identified at least 3 patterns from the repo's own CLAUDE.md worth adapting
- [ ] `skills/fme-workspace-authoring.md` created with all sections present
- [ ] `instincts/fme-instincts.md` created with at least 4 instincts
- [ ] `memory/fme-project-context.md` created and populated with real project context

#### Execution Validation
- [ ] Control run completed with the original benchmark task
- [ ] Treatment run completed with the **identical** prompt
- [ ] Both runs logged with iteration counts
- [ ] Token usage captured for both runs (even if approximate)

#### Analysis Validation
- [ ] `scorecard.md` fully completed for both runs
- [ ] Delta row calculated for iterations, cost, and quality
- [ ] A written "Key Finding" paragraph exists (not a template placeholder)
- [ ] A decision is recorded (adopt / hybrid / no change / more data needed)

#### The Acid Test

Run this self-check:

```
Can you answer these three questions from memory?
  1. In the treatment run, did Claude apply the Research-First Protocol? 
     How do you know?
  2. What was the iteration count delta?
  3. Based on your data, would you adopt skills/instincts for your next 
     Globe & Atlas workspace task?
```

If you can answer all three clearly, you've completed the exercise with full understanding.

---

## 5. Next Steps

### Immediate (This Week)

**5.1 — Run a Second Benchmark Task**

One data point is anecdote. Two starts to be pattern. Pick a different FME task — ideally one that:
- Is *more complex* than the first (more transformers, Python callout required)
- Or tests a *different task type* (debugging an existing workspace vs. building new)

Add a Run 3 to your scorecard and see if the delta holds.

**5.2 — Refine Your Skills File**

After the benchmark, you almost certainly noticed gaps. Update `fme-workspace-authoring.md`:

```bash
# Add to the "Patterns" section any transformer chains that worked well
# Tighten anti-patterns based on mistakes Claude made
# Add any Globe & Atlas-specific vocabulary that was missing
```

### Short Term (Next 2–4 Weeks)

**5.3 — Build a Skills Library**

Your FME work likely spans several recurring sub-domains. Consider separate skill files for each:

```
skills/
├── fme-workspace-authoring.md     ← already built
├── fme-python-callouts.md         ← Python scripting patterns
├── fme-postgis-integration.md     ← PostGIS-specific reader/writer configs
├── fme-coordinate-systems.md      ← CRS transformation patterns
└── fme-debugging.md               ← Diagnosing workspace failures
```

**5.4 — Implement Persistent Memory Properly**

The memory seed file you created is static. Look at the `memory/` directory in everything-claude-code for patterns on:
- How to structure memory for append-over-time (not just read-once)
- Session end prompts that extract learnings back into memory files
- How to avoid memory files becoming bloated/noisy

**5.5 — Measure Token Overhead of Skills Files**

Your treatment CLAUDE.md is larger — calculate the overhead:

```bash
# Rough token estimate: ~4 characters per token
wc -c skills/fme-workspace-authoring.md instincts/fme-instincts.md memory/fme-project-context.md
# Divide total chars by 4 for approximate token count
# This is your per-session overhead cost — is it paid back in fewer iterations?
```

### Medium Term (Next Quarter)

**5.6 — Contribute Back to everything-claude-code**

Your FME skills module is genuinely novel — the repo doesn't have geospatial/ETL domain skills. Consider:
- Opening a PR with your FME skill as an example domain module
- Filing an issue if you found the harness pattern unclear or missing features

**5.7 — Automate the Benchmark**

Once you have 5+ data points, create a lightweight benchmark runner:

```bash
#!/bin/bash
# benchmark-run.sh
# Usage: ./benchmark-run.sh "task description" control|treatment

TASK="$1"
MODE="$2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="runs/${MODE}_${TIMESTAMP}.log"

echo "=== Benchmark Run: $MODE ===" > "$LOG_FILE"
echo "Task: $TASK" >> "$LOG_FILE"
echo "Start: $(date)" >> "$LOG_FILE"

# Launch Claude Code in the appropriate directory
cd "runs/$MODE"
claude --print "Benchmark task: $TASK" | tee -a "../../$LOG_FILE"

echo "End: $(date)" >> "$LOG_FILE"
```

**5.8 — Apply the Pattern Beyond FME**

The skills/instincts/memory pattern is domain-agnostic. Once validated for FME, ask:
- What other recurring Claude Code tasks do you do where this pattern would help?
- Globe & Atlas frontend work? Data QA scripts? Documentation generation?

Each new domain you apply it to is another Tool Critic data point about where structured prompting earns its overhead vs. where a simple CLAUDE.md stays leaner and faster.

---

## Appendix: Quick Reference

### Key Files Created in This Exercise

```
~/projects/fme-claude-benchmark/
├── scorecard.md                          ← Your benchmark results
├── control-log.md                        ← Control run iteration log
├── skills/
│   └── fme-workspace-authoring.md        ← FME domain skill
├── instincts/
│   └── fme-instincts.md                  ← FME heuristics
├── memory/
│   └── fme-project-context.md            ← Project memory seed
└── runs/
    ├── control/
    │   ├── CLAUDE.md                     ← Your original directive
    │   └── output/                       ← Control run outputs
    └── treatment/
        ├── CLAUDE.md                     ← Skills/instincts loader
        └── output/                       ← Treatment run outputs
```

### The Core Insight to Carry Forward

> A `CLAUDE.md` directive tells Claude *who it is in this session*.  
> A skills/instincts module tells Claude *how to think before it acts*.  
> Memory tells Claude *what it already knows*.  
> The delta you measured tells you *which layer of that stack is worth the overhead for your specific work*.