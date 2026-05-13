# Wire claude-mem into Your Claude Code CLI for FME Session Persistence

## A Practical Tutorial for GIS/ETL Workflow Automation

---

## 1. Introduction & Context

### What Is This?

`claude-mem` is a Claude Code plugin developed by [@thedotmack](https://github.com/thedotmack) that solves one of the most frustrating pain points in long-running AI-assisted development: **Claude Code forgets everything when you close a session.**

Every time you open a new Claude Code CLI session, you start from zero. You re-explain your FME workspace structure, re-describe your ETL conventions, re-establish which Streamlit patterns you prefer. This cognitive overhead compounds across weeks of work.

`claude-mem` breaks this cycle by:

1. **Capturing** key decisions, context, and patterns from each session
2. **Compressing** them using Claude's agent SDK into dense, relevant summaries
3. **Injecting** relevant prior context back into future sessions automatically

### Why This Matters for FME Workflow Automation

If you're using Claude Code CLI to assist with multi-session FME workspace development, you've likely already built a `CLAUDE.md` file as a manual workaround — documenting your conventions, workspace naming schemes, transformer preferences, and ETL pipeline patterns by hand.

The `claude-mem` plugin automates and enhances this approach:

| Approach | Effort | Freshness | Coverage |
|---|---|---|---|
| Manual `CLAUDE.md` | High (you write everything) | Stale (you update manually) | Only what you remember to document |
| `claude-mem` | Low (automatic capture) | Current (updated each session) | Everything discussed in sessions |

This tutorial walks you through installing the plugin, running it across two FME workflow automation sessions, and documenting the delta between approaches in a structured Build post.

---

## 2. Prerequisites

### Required Tools

Before starting, confirm you have the following installed and configured:

```bash
# Verify Claude Code CLI is installed
claude --version

# Verify Node.js (required for claude-mem)
node --version   # Should be v18+

# Verify npm
npm --version

# Verify git (for cloning the plugin)
git --version
```

### Required Knowledge

- [ ] You've used Claude Code CLI for at least one FME-related session
- [ ] You have an existing FME workspace or ETL project you're actively developing
- [ ] You understand what your current `CLAUDE.md` contains (or you know you don't have one yet)
- [ ] You have a Globe & Atlas account or equivalent Build journal where you document your learning

### Required Setup

- [ ] A working `CLAUDE.md` file (even a minimal one — we'll use this as our baseline)
- [ ] At least two FME workflow sessions you can run back-to-back within this exercise
- [ ] Write access to your project directory

### Create a Baseline CLAUDE.md (If You Don't Have One)

If you don't already have a `CLAUDE.md`, create a minimal one now to use as your comparison baseline:

```bash
cat > CLAUDE.md << 'EOF'
# Project Context

## FME Workspace Conventions
- Workspace naming: [your convention here]
- Transformer preferences: [e.g., "Prefer AttributeCreator over AttributeRenamer for clarity"]
- Output format standards: [e.g., "All geodata outputs use EPSG:4326"]

## ETL Pipeline Patterns
- [Describe your standard input → transform → output pattern]
- [Note any common data sources: PostGIS, Esri, flat files, APIs]

## Active Development Focus
- [What are you currently building?]
- [What decisions were made last session?]

## Known Issues / Constraints
- [Anything Claude needs to know to avoid repeating mistakes]
EOF
```

---

## 3. Step-by-Step Guide

### Phase 1: Install claude-mem

#### Step 1.1 — Clone the Repository

```bash
# Navigate to your preferred tools directory
cd ~/tools  # or wherever you keep local tooling

# Clone claude-mem
git clone https://github.com/thedotmack/claude-mem.git
cd claude-mem
```

#### Step 1.2 — Install Dependencies

```bash
npm install
```

Expected output:
```
added 47 packages, and audited 48 packages in 3s
found 0 vulnerabilities
```

#### Step 1.3 — Build the Plugin

```bash
npm run build
```

#### Step 1.4 — Link Globally (Optional but Recommended)

```bash
npm link
```

This allows you to call `claude-mem` from any directory.

#### Step 1.5 — Verify Installation

```bash
claude-mem --version
# or
claude-mem --help
```

You should see the plugin's help output describing available commands.

---

### Phase 2: Configure claude-mem for Your FME Project

#### Step 2.1 — Initialize claude-mem in Your Project Directory

Navigate to your FME project directory and initialize the plugin:

```bash
cd /path/to/your/fme-project
claude-mem init
```

This creates a `.claude-mem/` directory in your project with configuration files:

```
your-fme-project/
├── .claude-mem/
│   ├── config.json          # Plugin configuration
│   ├── sessions/            # Raw session captures (auto-generated)
│   └── memory.md            # Compressed, injected context (auto-generated)
├── CLAUDE.md                # Your existing manual context
├── workspaces/              # Your FME workspaces
└── ...
```

#### Step 2.2 — Configure Session Capture Settings

Open `.claude-mem/config.json` and customize for your FME workflow context:

```json
{
  "project": {
    "name": "FME Workflow Automation",
    "domain": "GIS/ETL",
    "focus_keywords": [
      "FME",
      "workspace",
      "transformer",
      "ETL",
      "geodata",
      "PostGIS",
      "EPSG",
      "Streamlit"
    ]
  },
  "capture": {
    "auto_capture": true,
    "capture_on_exit": true,
    "max_session_tokens": 2000,
    "compression_strategy": "semantic"
  },
  "injection": {
    "auto_inject": true,
    "max_injected_tokens": 1500,
    "relevance_threshold": 0.7
  },
  "output": {
    "memory_file": ".claude-mem/memory.md",
    "append_to_claude_md": false
  }
}
```

> **Note on `append_to_claude_md`:** Keep this `false` for now. You want `claude-mem` to maintain its own `memory.md` so you can directly compare it against your manual `CLAUDE.md` at the end of this exercise.

#### Step 2.3 — Add .claude-mem to Your .gitignore (Decide Your Policy)

Consider whether session memory should be committed to version control:

```bash
# Option A: Ignore session captures, commit compressed memory
echo ".claude-mem/sessions/" >> .gitignore

# Option B: Ignore all claude-mem data (keep it local)
echo ".claude-mem/" >> .gitignore

# Option C: Commit everything (useful for team shared context)
# Don't add to .gitignore
```

For a solo FME project, **Option A** is recommended — sessions are ephemeral noise, but the compressed `memory.md` is valuable shared context.

---

### Phase 3: Run Session 1 — Your First Tracked FME Session

#### Step 3.1 — Start Claude Code with claude-mem Active

```bash
# From your FME project directory
claude-mem start

# Then in the same terminal, launch Claude Code
claude
```

Alternatively, if claude-mem supports a wrapper mode:

```bash
claude-mem run -- claude
```

Check the plugin's README for the exact invocation pattern, as this may vary by version.

#### Step 3.2 — Work on a Real FME Task

Conduct a genuine working session. Good candidates for Session 1:

- Building a new reader/writer pair in an FME workspace
- Debugging a transformer chain issue
- Designing an ETL pipeline for a new data source
- Writing a Python caller script for custom transformation logic

**Suggested prompts to use during Session 1** (these help claude-mem capture rich context):

```
"I'm working on an FME workspace that reads from PostGIS and outputs 
to a GeoJSON file. The workspace is called [name]. Help me structure 
the AttributeCreator transformer to standardize field names."
```

```
"We've decided to use EPSG:4326 for all output layers in this project. 
Please remember this convention going forward."
```

```
"The current challenge is that the FeatureMerger is dropping records 
when the join key has null values. Here's my current approach..."
```

> **Why this matters:** These types of domain-specific decisions are exactly what `claude-mem` is designed to capture — and what manual `CLAUDE.md` maintenance tends to miss between sessions.

#### Step 3.3 — End Session 1 Cleanly

```bash
# Exit Claude Code normally
exit

# Then stop claude-mem capture
claude-mem stop

# Optionally, review what was captured
claude-mem summary
```

#### Step 3.4 — Inspect the Session Capture

```bash
# View the raw session capture
cat .claude-mem/sessions/session-001.md

# View the compressed memory (what will be injected next session)
cat .claude-mem/memory.md
```

**Document what you observe:**

```bash
# Create a personal observation log for this exercise
cat >> exercise-log.md << 'EOF'
## Session 1 Observations

### What claude-mem captured:
- [ ] FME workspace conventions discussed
- [ ] Specific transformer decisions
- [ ] Data source/format preferences
- [ ] Active problems being solved
- [ ] Other: 

### What my manual CLAUDE.md has that claude-mem missed:
- 

### What claude-mem captured that my CLAUDE.md lacked:
- 
EOF
```

---

### Phase 4: Run Session 2 — Test Context Injection

#### Step 4.1 — Start a New Session (Simulate a Fresh Day)

Wait at least a few minutes, or close and reopen your terminal to simulate a realistic session gap.

```bash
# From your FME project directory
claude-mem start
claude
```

#### Step 4.2 — Test Context Retention Without Prompting

Open Claude Code and **do not manually provide context**. Instead, jump straight into work:

```
"Continue working on the FME workspace from our last session. 
What was the status of the FeatureMerger issue?"
```

```
"What EPSG code are we using for outputs in this project?"
```

```
"Remind me what we decided about the AttributeCreator field naming convention."
```

Observe how Claude Code responds. With `claude-mem` active and injecting prior context, it should answer these questions without you needing to re-explain.

#### Step 4.3 — Do Real Work in Session 2

Continue the FME development task from Session 1, or start a related task:

- Implement the solution to the FeatureMerger issue identified in Session 1
- Extend the workspace to add a new output format
- Write a Workspace Runner script that calls the workspace via CLI

**Pay attention to:**
- Does Claude Code reference Session 1 decisions without being told?
- Does it apply the conventions correctly (EPSG, naming, etc.)?
- Does it avoid suggesting approaches you explicitly rejected in Session 1?

#### Step 4.4 — End Session 2 and Capture

```bash
exit
claude-mem stop
claude-mem summary
```

---

### Phase 5: Compare and Document the Delta

#### Step 5.1 — Side-by-Side Comparison

```bash
# View your manual CLAUDE.md
cat CLAUDE.md

# View claude-mem's generated memory
cat .claude-mem/memory.md
```

Run a diff to see structural differences:

```bash
diff CLAUDE.md .claude-mem/memory.md
```

#### Step 5.2 — Fill Out Your Comparison Matrix

Create a structured comparison document:

```bash
cat > session-comparison.md << 'EOF'
# claude-mem vs Manual CLAUDE.md — Session Comparison

## Session 1 → Session 2 Context Retention Test

### Test Scenarios and Results

| Question Asked in Session 2 | With CLAUDE.md Only | With claude-mem | Winner |
|---|---|---|---|
| "What was the status of X issue?" | Had to re-explain | Recalled from Session 1 | |
| "What EPSG are we using?" | ✅ In CLAUDE.md | ✅ Auto-captured | |
| "What did we decide about Y?" | ❌ Not documented | ✅ Auto-captured | |
| [Add your own test] | | | |

### Qualitative Observations

**claude-mem captured these things I didn't have in CLAUDE.md:**
1. 
2. 
3. 

**My CLAUDE.md had these things claude-mem missed or got wrong:**
1. 
2. 
3. 

**Context injection quality (1-5):** ___
**Compression accuracy (did it get the details right?):** ___
**Setup effort vs. benefit ratio:** ___

### Time Savings Estimate
- Time spent maintaining CLAUDE.md manually (per session): ___ minutes
- Time spent reviewing/correcting claude-mem output: ___ minutes
- Net time saved per session: ___ minutes
- Projected monthly savings (est. X sessions/month): ___ minutes

### Recommendation
[ ] Replace CLAUDE.md with claude-mem entirely
[ ] Use claude-mem to augment CLAUDE.md  
[ ] Use claude-mem for session context, CLAUDE.md for static conventions
[ ] Not worth the complexity for my workflow
EOF
```

#### Step 5.3 — Draft Your Globe & Atlas Build Post

Use this template to structure your Build post:

```markdown
# Build Post: claude-mem for FME Session Persistence

## What I Built / Tested
Wired the `claude-mem` Claude Code plugin into my FME workflow 
automation setup to test whether it could replace or augment my 
manual CLAUDE.md approach for multi-session context retention.

## The Problem I Was Solving
[Describe your specific pain point — e.g., "I was spending 5-10 minutes 
at the start of every FME session re-explaining my workspace conventions 
to Claude Code..."]

## What I Did
1. Installed claude-mem from github.com/thedotmack/claude-mem
2. Configured it for my FME project context
3. Ran two consecutive FME workflow sessions with memory capture active
4. Compared context retention against my existing CLAUDE.md

## Results

### What Worked Well
- [Specific example of good context retention]
- [Specific decision that was correctly recalled]

### What Didn't Work / Gaps
- [Specific example of missed or incorrect context]
- [Any setup friction worth noting]

## The Delta vs. Manual CLAUDE.md

[Paste or summarize your comparison matrix]

## My Recommendation
[Based on your test, what would you tell someone in a similar workflow?]

## Next Steps
[What will you change in your workflow based on this?]

## Resources
- claude-mem: https://github.com/thedotmack/claude-mem
- Claude Code CLI: https://docs.anthropic.com/claude-code
```

---

## 4. Validation

### How to Know You Completed This Exercise Successfully

Work through this checklist:

#### Installation Validation
```bash
# ✅ claude-mem is installed and responds
claude-mem --help

# ✅ Plugin initialized in your project
ls -la .claude-mem/

# ✅ Configuration is customized (not just defaults)
cat .claude-mem/config.json | grep "FME\|GIS\|your project name"
```

#### Session Capture Validation
```bash
# ✅ Session 1 capture exists
ls .claude-mem/sessions/

# ✅ Compressed memory was generated
cat .claude-mem/memory.md | wc -l  # Should have meaningful content
```

#### Context Retention Validation

You've successfully validated context injection if **at least 3 of these are true** after Session 2:

- [ ] Claude Code correctly stated the EPSG convention from Session 1 without prompting
- [ ] Claude Code recalled the status of at least one specific FME issue from Session 1
- [ ] Claude Code referenced a naming convention or architectural decision from Session 1
- [ ] Claude Code avoided a mistake you had explicitly corrected in Session 1
- [ ] Claude Code's opening response showed awareness of your active project context

#### Documentation Validation

- [ ] `session-comparison.md` is filled out with real observations (not hypothetical)
- [ ] Build post draft exists with at least 200 words of genuine reflection
- [ ] Build post is published (or scheduled) in Globe & Atlas

### Quick Smoke Test

Run this diagnostic to confirm the full loop is working:

```bash
# Check session count
ls .claude-mem/sessions/ | wc -l
# Expected: 2 (one per session you ran)

# Check memory file was updated
stat .claude-mem/memory.md
# Expected: modification time should be recent

# Confirm memory has project-relevant content
grep -i "FME\|workspace\|ETL\|transformer" .claude-mem/memory.md
# Expected: multiple matches
```

---

## 5. Next Steps

### Immediate (This Week)

1. **Run a third session** to see if memory compounds correctly — does Session 3 benefit from Sessions 1 and 2 combined?

2. **Tune the relevance threshold** in `config.json` — if injection is noisy, raise `relevance_threshold` to `0.8`; if it's missing things, lower it to `0.6`

3. **Decide on your hybrid strategy** — most practitioners land on:
   - `CLAUDE.md` → Static conventions, project architecture, explicit rules (you maintain this)
   - `claude-mem/memory.md` → Dynamic session context, recent decisions, active issues (auto-maintained)

### Short Term (Next 2-4 Weeks)

4. **Test across a Streamlit build session** — apply the same comparison methodology to your Streamlit app development work and see if retention patterns differ from FME sessions

5. **Explore memory pruning** — as `.claude-mem/memory.md` grows, experiment with the plugin's compression settings to keep injected context under the token limit without losing important history

6. **Create a session start ritual** — even with `claude-mem` active, a brief structured prompt at session start helps:
   ```
   "claude-mem context loaded. Today's focus: [X]. Continue from where we left off."
   ```

### Longer Term

7. **Contribute upstream** — if you find gaps in how `claude-mem` handles GIS/ETL-specific terminology or FME workspace patterns, consider opening an issue or PR on [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)

8. **Evaluate team use cases** — if you collaborate with others on FME workspaces, explore whether committing `memory.md` to version control creates a useful shared context layer for the whole team

9. **Build a session summary habit** — regardless of whether you continue using `claude-mem`, the act of ending each session with a structured summary is a high-value practice:
   ```
   "Before we close: summarize the 3 most important decisions we made today 
   and what's blocked or pending. I'll use this to start tomorrow's session."
   ```

---

## Reference: Troubleshooting Common Issues

### Plugin not capturing session content

```bash
# Verify claude-mem process is running during your Claude Code session
ps aux | grep claude-mem

# Check for permission issues
ls -la .claude-mem/sessions/
```

### Memory injection not appearing in Claude Code

```bash
# Verify auto_inject is enabled
cat .claude-mem/config.json | grep auto_inject

# Check that memory.md has content
wc -l .claude-mem/memory.md

# Try manual injection
claude-mem inject --session-file .claude-mem/memory.md
```

### Memory file growing too large

```bash
# Check current size
wc -c .claude-mem/memory.md

# Manually trigger compression
claude-mem compress --max-tokens 1500

# Adjust config
# Set "max_injected_tokens": 1000 for more aggressive compression
```

### Claude Code ignoring injected context

This often means the injection is happening but the context isn't being treated as high-priority. Try prepending memory content to your first prompt manually:

```bash
# Export memory as a variable
MEMORY=$(cat .claude-mem/memory.md)
echo "Session context: $MEMORY" | pbcopy  # macOS
# Then paste at the start of your first Claude Code prompt
```

---

*Last updated for claude-mem v0.x | Claude Code CLI | FME 2024+*