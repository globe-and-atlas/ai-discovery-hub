# Add `claude-mem` Persistence to Your Sentinel Hub Scripting Sessions

**Tutorial type:** Hands-on lab | **Effort:** Medium (~2–3 hours across three sessions) | **Audience:** GIS/AI practitioners using Claude Code CLI with Sentinel Hub APIs

---

## 1. Introduction & Context

Every time you close a Claude Code session and open a new one, the slate is wiped clean. For ad-hoc queries that's fine. For iterative Sentinel Hub scripting — where you're tuning `evalscript` parameters, debugging OGC service endpoints, calibrating cloud-mask thresholds, and juggling multiple AOIs across days — that amnesia creates real friction. You re-explain your coordinate systems. You re-paste your `instanceId`. You re-correct the same misunderstanding about `mosaicking` order. Every session costs you correction prompts before you reach productive output.

**`claude-mem`** (v6.5.0, Apache 2.0) is a persistent memory compression layer built specifically for Claude Code. It works by:

1. **Capturing** tool-usage observations and decisions made during a session.
2. **Compressing** them into semantic summaries with AI.
3. **Injecting** relevant summaries back into the context window at the start of future sessions.

For a Sentinel Hub practitioner, this means Claude Code can "remember" that:
- Your default AOI is a specific bounding box in WGS84.
- You prefer `BYOC` collections over public ones for your project.
- The `dataMask` band must always be included in your evalscript output.
- You hit a rate-limit bug on the Process API last Tuesday and worked around it.

This tutorial walks you through three consecutive Sentinel Hub scripting sessions — one baseline (no memory), two with `claude-mem` active — and gives you a repeatable scoring method to measure whether the tool cuts correction-prompt friction by 30% or more, the threshold at which you'll document it as a recommended tool for other GIS practitioners.

---

## 2. Prerequisites

Before you start, confirm you have everything below. Items marked **[required]** will block you if missing.

### Software

| Requirement | Version | Check command |
|---|---|---|
| **Node.js** [required] | ≥ 18.0.0 | `node --version` |
| **npm** [required] | ≥ 8.0.0 | `npm --version` |
| **Claude Code CLI** [required] | latest | `claude --version` |
| **Git** | any | `git --version` |

### Accounts & API keys

- **Anthropic API key** — Claude Code must already be authenticated (`claude auth status` returns your account).
- **Sentinel Hub account** — You need a `CLIENT_ID`, `CLIENT_SECRET`, and at least one active `instanceId` (or a configured BYOC collection). A free trial account is sufficient.

### Domain knowledge assumed

- You have run at least one Sentinel Hub Process API call (REST or Python SDK).
- You are comfortable writing simple evalscripts (JavaScript-style band math).
- You know what a BBOX, time range, and `mosaicking` order are in Sentinel Hub terms.

### Working directory setup

Create a clean project folder you'll use for all three sessions:

```bash
mkdir ~/sh-claude-lab && cd ~/sh-claude-lab
```

Initialize a minimal project structure:

```bash
mkdir -p evalscripts logs metrics
touch CLAUDE.md   # Claude Code's project-level context file
```

Add a stub to `CLAUDE.md` so Claude Code knows the domain upfront (you'll expand this later):

```markdown
# Sentinel Hub Scripting Project

## Project type
Remote sensing / EO data scripting via Sentinel Hub Process API.

## Default settings
- CRS: EPSG:4326
- Default AOI: [your bounding box here, e.g. 13.0,47.0,14.5,48.5 — update before Session 1]
- Preferred data source: Sentinel-2 L2A
- Output format: image/tiff

## Key constraints
- Always include dataMask band in evalscript output array.
- Use mosaicking: LEAST_CC (least cloud coverage) unless otherwise stated.
- API endpoint: https://services.sentinel-hub.com
```

> **Update the AOI** to a bounding box relevant to your actual work before proceeding. Keep it small enough that test requests return quickly.

---

## 3. Step-by-Step Guide

### Phase A — Baseline Session (No Memory)

Run this session **before** installing `claude-mem`. Its purpose is to establish a correction-prompt baseline count.

#### Step A1: Set up your session metrics log

You will track one simple metric per session:

> **Correction Prompt Count (CPC)** — the number of prompts you had to send to fix, re-explain, or re-constrain something Claude Code got wrong or forgot.

Create your tracking file:

```bash
cat > metrics/session_log.md << 'EOF'
# Session Metrics Log

## Session 1 — Baseline (no claude-mem)
- Date:
- Task:
- Total prompts sent:
- Correction prompts (CPC):
- Notes:

## Session 2 — With claude-mem
- Date:
- Task:
- Total prompts sent:
- Correction prompts (CPC):
- Notes:

## Session 3 — With claude-mem
- Date:
- Task:
- Total prompts sent:
- Correction prompts (CPC):
- Notes:
EOF
```

#### Step A2: Run baseline Session 1

Open Claude Code in your project directory:

```bash
cd ~/sh-claude-lab
claude
```

Run the following scripting task. Keep a tally mark in a notepad (physical or digital) every time you send a correction prompt.

**Session 1 task script — paste these prompts sequentially into Claude Code:**

```
Prompt 1:
Write a Sentinel Hub Process API evalscript that returns a true-color RGB composite
from Sentinel-2 L2A. Use bands B04, B03, B02, normalized to [0,1] range.
Include a dataMask output band.
```

```
Prompt 2:
Now build the full JSON request body for the Process API to fetch a 512x512 pixel
image over my project AOI for 2024-06-01 to 2024-06-30. Use least-cloud mosaicking.
Output format should be image/tiff.
```

```
Prompt 3:
Write a Python function using the `requests` library that authenticates to Sentinel Hub
using client credentials OAuth2, then calls the Process API with that request body.
Handle HTTP 429 rate-limit responses with exponential backoff (max 3 retries).
```

```
Prompt 4:
The evalscript in the request body needs to be a single-line JSON-escaped string.
Fix the request body you generated so the evalscript value is properly escaped.
```

> **Tally rule:** Every time you need to send a prompt that corrects, re-clarifies, or re-specifies something — including prompts like Prompt 4 above — count it. Prompts that simply advance the task to the next logical step do not count.

After the session, record your numbers:

```bash
# Example — edit with your actual counts
# Total prompts sent: 6
# Correction prompts (CPC): 3
# CPC rate: 3/6 = 50%
```

Save the evalscript and Python function to your project:

```bash
# Ask Claude Code to write the files before ending the session
# "Save the evalscript to evalscripts/true_color.js and the Python function
#  to scripts/fetch_image.py"
```

Exit Claude Code (`Ctrl+D` or type `/exit`).

---

### Phase B — Install `claude-mem`

#### Step B1: Install globally using the official one-liner

From the source material, the canonical install command is:

```bash
npx claude-mem install
```

That's it. This command:
- Installs the `claude-mem` package.
- Detects your Claude Code installation (looks for `~/.claude`).
- Wires up the MCP hooks that capture and inject session context automatically.

Expected output will confirm installation. You should see something confirming Claude Code was detected and hooks were registered.

> **Source note:** The source material specifies `npx claude-mem install` as the complete install command for Claude Code. No additional flags are needed for the default Claude Code target. The `--ide` flag is only required for Gemini CLI (`--ide gemini-cli`) or OpenCode (`--ide opencode`).

#### Step B2: Verify the installation

Restart Claude Code and check that memory context injection is active:

```bash
cd ~/sh-claude-lab
claude
```

At the Claude Code prompt, type:

```
/memory status
```

> **Note:** The source material confirms `claude-mem` is MCP-based and integrates with Claude Code's plugin system. If `/memory status` is not a recognized command in your version, look for confirmation in the session startup banner — `claude-mem` should announce itself or inject a context header. If neither appears, see the Troubleshooting section below.

Alternatively, you can verify via the plugin marketplace path mentioned in the source:

```bash
# If you need to re-install or verify via plugin system:
# Inside Claude Code, type:
# /plugin install claude-mem
```

Exit Claude Code for now.

---

### Phase C — Session 2 (With Memory, Continuation Task)

This session continues directly from where Session 1 left off. The goal is to measure how much context `claude-mem` carries forward without you re-explaining it.

#### Step C1: Open a fresh Claude Code session

```bash
cd ~/sh-claude-lab
claude
```

Observe the session startup. `claude-mem` should inject a summary of Session 1 context into the window. Note what it remembered.

#### Step C2: Run Session 2 task

Again, tally correction prompts separately.

**Session 2 task script:**

```
Prompt 1:
Extend the Python function from our last session to support NDVI output instead of
true-color RGB. Update the evalscript to calculate (B08 - B04) / (B08 + B04) and
return it as a single-band float32 tiff with the dataMask band.
```

```
Prompt 2:
Add a second function that takes the fetched NDVI tiff and uses rasterio to
calculate basic statistics: min, max, mean, and the percentage of valid pixels
(where dataMask == 1).
```

```
Prompt 3:
Now write a CLI wrapper using argparse so I can call the script like:
  python fetch_ndvi.py --start 2024-06-01 --end 2024-06-30 --output ./output/
```

```
Prompt 4:
Add a --dry-run flag that prints the full API request body as JSON without sending it,
for debugging purposes.
```

> **Watch for:** Did Claude Code remember your AOI without you re-specifying it? Did it remember the `dataMask` requirement without being told? Did it remember the OAuth2 auth pattern? Each thing it correctly remembered without prompting is a friction point saved.

Save outputs and record metrics:

```bash
# Record in metrics/session_log.md:
# Total prompts sent:
# Correction prompts (CPC):
```

Exit Claude Code.

---

### Phase D — Session 3 (With Memory, New but Related Task)

Session 3 tests whether `claude-mem` handles a task pivot — same project context, different scripting goal. This is the harder test.

#### Step D1: Open a fresh Claude Code session

```bash
cd ~/sh-claude-lab
claude
```

Again, note what context `claude-mem` injected.

#### Step D2: Run Session 3 task

**Session 3 task script:**

```
Prompt 1:
I want to add multi-temporal support to our Sentinel Hub tooling. Write a function
that loops over a list of monthly date ranges for a full year (2024-01 through 2024-12)
and calls the NDVI fetch function for each month, saving each output tiff with a
filename that includes the year-month.
```

```
Prompt 2:
Add basic error handling so that if a month's API call fails, the script logs the
error to a file called errors.log, skips that month, and continues to the next.
```

```
Prompt 3:
Write a summary function that reads all the monthly NDVI tiffs in the output directory
and produces a CSV with columns: year_month, min_ndvi, max_ndvi, mean_ndvi, valid_pixel_pct.
```

```
Prompt 4:
The CSV output should also include a column for cloud_cover_pct. Update the Process API
request to use the Statistical API endpoint instead, which returns cloud cover metadata
alongside the NDVI statistics. If you need the Statistical API endpoint format, use:
https://services.sentinel-hub.com/api/v1/statistics
```

> **Watch for the same signals:** Re-explanations needed? Did Claude Code correctly reuse the OAuth2 pattern, the AOI, the `dataMask` convention, the rate-limit backoff logic?

Record your metrics and exit.

---

### Phase E — Calculate Friction Reduction

With three sessions logged, calculate your friction reduction metric.

#### Step E1: Fill in your scorecard

Open `metrics/session_log.md` and compute the following:

```markdown
## Friction Reduction Scorecard

### Baseline (Session 1)
- CPC:        [e.g., 3]
- Total:      [e.g., 6]
- CPC rate:   [e.g., 50%]

### With claude-mem (Sessions 2 + 3 combined)
- CPC:        [e.g., 2]  ← sum of S2 and S3 correction prompts
- Total:      [e.g., 8]  ← sum of S2 and S3 total prompts
- CPC rate:   [e.g., 25%]

### Friction reduction
= (Baseline CPC rate - Memory CPC rate) / Baseline CPC rate × 100
= (50% - 25%) / 50% × 100
= 50% reduction  ✅  exceeds 30% threshold
```

#### Step E2: Apply the 30% decision rule

```
IF friction_reduction >= 30%:
  → Proceed to Tool Critic documentation (Phase F)
ELSE:
  → Review what context was NOT being carried forward (see Troubleshooting)
  → Consider adding more explicit context to CLAUDE.md and re-running Session 3
```

---

### Phase F — Document for Tool Critic Post (If Threshold Met)

If your friction reduction is ≥ 30%, document the setup for other GIS practitioners.

#### Step F1: Create your setup documentation file

```bash
cat > docs/claude-mem-setup-for-gis.md << 'EOF'
# Using claude-mem with Claude Code for Sentinel Hub Scripting

## What this solves
[Describe the stateless session problem in your own words based on your experience]

## Install
```bash
npx claude-mem install
```
Restart Claude Code. Memory injection is automatic from the next session onward.

## Observed friction reduction
- Baseline CPC rate (no memory): [your number]%
- With claude-mem CPC rate: [your number]%
- Reduction: [your number]%
- Test methodology: [3-session Sentinel Hub scripting tasks — true-color RGB, NDVI,
  multi-temporal analysis]

## What it remembered correctly (saves the most time)
- [e.g., Project AOI bounding box — never had to re-paste it]
- [e.g., dataMask requirement in evalscript outputs]
- [e.g., OAuth2 client credentials flow pattern]
- [e.g., Exponential backoff strategy for 429 rate limits]

## What it did NOT carry forward (still needs manual context)
- [e.g., Specific collection IDs — always re-specify these]
- [e.g., ...]

## Recommendation for GIS practitioners
[Your honest assessment]

## Setup notes
- Node.js ≥ 18.0.0 required
- No configuration file needed for default Claude Code setup
- Works alongside CLAUDE.md (they complement each other — CLAUDE.md for static
  project constants, claude-mem for dynamic session learnings)
- Source: https://github.com/thedotmack/claude-mem
EOF
```

---

## 4. Validation

Use this checklist to confirm you have completed the exercise correctly:

### Installation validation

```bash
# 1. Confirm Node version meets requirement
node --version
# Must output v18.x.x or higher

# 2. Confirm claude-mem was installed (check for MCP registration)
# Inside Claude Code, at startup look for memory context injection header
# OR run:
claude
# Then at the prompt type: /mcp list
# claude-mem should appear in the registered MCP servers
```

### Session data validation

```bash
# 3. Confirm session context files exist
# claude-mem stores memory in your home directory (location managed by the tool itself)
# Check that something was captured after Session 1 by looking for the memory store:
ls ~/.claude/
# You should see claude-mem related files or directories created after Session 1
```

> **Source note:** The exact path of `claude-mem`'s memory store is managed internally by the tool. The source material does not specify the storage path explicitly. If you need to find it, run `npx claude-mem --help` after installation to check for a `--show-config` or similar flag. The tutorial cannot specify this path without risking inaccuracy.

### Functional validation

```bash
# 4. Confirm context injection happened in Session 2
# In your metrics/session_log.md, you should have a note under Session 2
# of at least ONE thing Claude Code correctly remembered from Session 1
# without being told. If the note is blank, memory injection did not work —
# see Troubleshooting.

# 5. Confirm your three script files exist
ls evalscripts/true_color.js
ls scripts/fetch_image.py
ls scripts/fetch_ndvi.py
```

### Metric validation

```bash
# 6. Confirm your scorecard is filled in
grep "Friction reduction" metrics/session_log.md
# Should return a line with a calculated percentage
```

### Pass criteria summary

| Check | Pass condition |
|---|---|
| Node version | ≥ 18.0.0 |
| `claude-mem` installed | Appears in MCP list or injects context at startup |
| Three sessions completed | All tasks produced working code files |
| Metrics recorded | CPC counts logged for all three sessions |
| Friction reduction calculated | Formula applied, result documented |
| Tool Critic doc created | Only if threshold ≥ 30% met |

---

## 5. Troubleshooting

### `claude-mem` not injecting context in Session 2

**Symptom:** Session 2 starts with no memory banner and Claude Code has no knowledge of Session 1.

**Likely causes and fixes:**

1. **Didn't restart Claude Code after install.** The source material explicitly states: *"Restart Claude Code or Gemini CLI. Context from previous sessions will automatically appear in new sessions."* Exit fully and relaunch.

2. **Session 1 ended too quickly.** `claude-mem` needs tool-usage activity to capture. If Session 1 was very short or you didn't actually generate code (only chatted), there may be nothing to compress. Re-run Session 1 with explicit code generation tasks.

3. **MCP server not registered.** Inside Claude Code, check `/mcp list`. If `claude-mem` is absent, re-run the install:
   ```bash
   npx claude-mem install
   ```

### `npx claude-mem install` fails

**Symptom:** Permission errors or package-not-found.

**Fix:**
```bash
# Ensure npm global prefix is writable, then retry:
npx --yes claude-mem install

# If behind a corporate proxy, ensure npm proxy settings are configured:
npm config list | grep proxy
```

### Low friction reduction (< 30%)

**Symptom:** claude-mem is working but your CPC rate didn't drop enough.

**Possible causes:**
- Your `CLAUDE.md` already covered most static context (good! — that means CLAUDE.md was doing heavy lifting, not a claude-mem failure).
- Your tasks were too independent between sessions for memory to be useful.
- Try making Session 3 more explicitly depend on Session 2 artifacts.

**Recommended action:** Add a fourth session that is a direct bug-fix or extension of Session 3 code. Continuation tasks should show the highest friction reduction.

---

## 6. Next Steps

### Immediate follow-on actions

1. **Publish your Tool Critic post.** Use `docs/claude-mem-setup-for-gis.md` as your draft. Focus on the specific Sentinel Hub context items that were and weren't carried forward — that specificity is what makes it useful to other GIS practitioners over generic AI tooling reviews.

2. **Add `claude-mem` to your standard Claude Code project template.** Since it installs once globally, any future Sentinel Hub project automatically benefits. Pair it with a well-structured `CLAUDE.md` for maximum effect:
   - `CLAUDE.md` → static project constants (AOI, collection IDs, API endpoints, naming conventions)
   - `claude-mem` → dynamic session learnings (bugs encountered, decisions made, patterns established)

3. **Test with longer session gaps.** The most valuable signal is whether `claude-mem` retains context across days or weeks. Schedule a follow-up Session 4 two weeks from now with a new but related task and measure whether your CPC rate holds low.

4. **Explore the MCP search tools.** The source material references `#mcp-search-tools` in the `claude-mem` documentation. Inside Claude Code, you may be able to query your memory store directly — useful for asking "what did we decide about mosaicking order?" without starting a full scripting task.

### Broader tool chain exploration

- **`CLAUDE.md` optimization** — Review the [Claude Code documentation](https://claude.com/claude-code) on project-level context files. A well-structured `CLAUDE.md` and `claude-mem` are complementary, not competing.
- **Multi-agent pipelines** — If you're orchestrating multiple Claude API calls (`claude-sonnet-4-6`, `claude-haiku-4-5`) for automated EO processing, consider whether `claude-mem`'s context compression could be injected as a system prompt prefix in your agent orchestration layer rather than only through the Claude Code CLI.
- **Alternative install paths** — The source material also shows a plugin marketplace install path:
  ```
  /plugin marketplace add thedotmack/claude-mem
  /plugin install claude-mem
  ```
  Test whether this provides any different behavior compared to the `npx` install for your specific Claude Code version.

### Tool Critic post structure suggestion

If your threshold was met, structure your post around this GIS-practitioner-specific angle:

```
1. The problem: EO scripting is highly stateful — AOIs, collections, 
   evalscript conventions, auth patterns, discovered bugs. Claude Code's 
   amnesia is a real cost.
2. The install: one command, no config.
3. Your test methodology: 3 sessions, CPC metric, 30% threshold.
4. Your results: [your actual numbers].
5. What it remembered: [your specific list].
6. What it missed: [your honest list].
7. Recommendation: conditional (or unconditional) based on your results.
```

---

*Tutorial based on `thedotmack/claude-mem` v6.5.0. All commands derived from the official repository at [github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem). Steps not covered by the source material are marked explicitly.*