# Spec-Driven Development for FME Workflows with Claude Code

## A Practical Tutorial: Replacing Vibe-Coding with Structured AI-Assisted Development

---

## 1. Introduction & Context

### What Is This?

This tutorial teaches you to apply **Spec-Driven Development (SDD)** — a disciplined, document-first approach to AI-assisted coding — to your existing FME workflow automation. Instead of firing off free-form prompts to Claude Code and hoping for usable output ("vibe-coding"), you write a formal specification *first*, then use that spec as the authoritative contract that drives every Claude Code interaction.

The workflow borrows directly from **Traycer's Epic Mode** approach: treating AI code generation like a junior developer who needs unambiguous requirements, not a mind-reader who can infer intent from casual conversation.

### Why Does This Matter for FME Work?

FME workflows sit at the intersection of several failure modes for vibe-coding:

- **Complex I/O contracts**: Coordinate systems, geometry types, attribute schemas, and projection details must be exactly right
- **Silent failures**: A pipeline that runs without errors but produces subtly wrong geometries or missing attributes can corrupt downstream data
- **Repeatability requirements**: Sentinel Hub pulls, GeoJSON transformations, and ETL pipelines need to behave identically across runs
- **Integration surface area**: FME scripts often talk to APIs, databases, file systems, and Streamlit dashboards simultaneously

Vibe-coding produces output that *looks* right. Spec-driven development produces output that *is* right — and gives you a paper trail to prove it.

### What You'll Build

By the end of this tutorial, you will have:

1. A formal spec document for one real FME workflow (Sentinel Hub pull or GeoJSON pipeline)
2. A Claude Code session driven entirely by that spec
3. A working, validated FME automation script
4. A documented comparison between your spec-driven output and your previous vibe-coded baseline
5. A reusable spec template you can apply to future workflows

---

## 2. Prerequisites

### Technical Requirements

| Requirement | Details |
|---|---|
| **Claude Code CLI** | Installed and authenticated (`npm install -g @anthropic-ai/claude-code` or via Anthropic's installer) |
| **FME Desktop** | Version 2022.x or later, with Python scripting enabled |
| **Python 3.9+** | For FME script execution outside Workbench |
| **A baseline FME workflow** | Something you've already built or attempted — Sentinel Hub pull, GeoJSON transform, or similar |
| **Text editor** | VS Code recommended (Claude Code integrates cleanly) |

### Knowledge Prerequisites

- You've used Claude Code CLI before (even casually/for vibe-coding)
- You understand what your target FME workflow does at a functional level
- Basic familiarity with JSON Schema or structured documentation (helpful but not required)

### Mindset Prerequisite

You need to accept one uncomfortable truth before continuing:

> **Writing the spec will feel slower than just prompting Claude. It is slower — upfront. The payoff comes at review, debugging, and the third time you re-run this workflow six months from now.**

If you're not willing to spend 30–45 minutes on specification before touching Claude Code, this exercise will not deliver its full value.

### Setup Check

Run these commands to confirm your environment is ready:

```bash
# Verify Claude Code CLI
claude --version

# Verify Python
python3 --version

# Confirm FME scripting path is accessible (adjust for your install)
fme --version 2>/dev/null || echo "FME not in PATH — that's fine, note your FME install directory"

# Create a working directory for this exercise
mkdir -p ~/fme-spec-driven/specs
mkdir -p ~/fme-spec-driven/scripts
mkdir -p ~/fme-spec-driven/validation
mkdir -p ~/fme-spec-driven/docs
cd ~/fme-spec-driven
```

---

## 3. Step-by-Step Guide

### Phase 1: Audit Your Baseline (20 minutes)

Before writing a single line of spec, document *exactly* what your current vibe-coded approach looks like. This is your comparison baseline.

#### Step 1.1 — Record Your Current Prompt Pattern

Open a file called `baseline.md` and honestly document how you currently use Claude Code for this workflow:

```bash
touch ~/fme-spec-driven/docs/baseline.md
```

Fill it in using this template:

```markdown
# Baseline: Vibe-Coding Audit

## Date
[Today's date]

## Workflow Being Automated
[e.g., "Sentinel Hub Sentinel-2 L2A pull for AOI bounding box, export to GeoTIFF"]

## What I Currently Prompt Claude With
[Paste your actual prompt(s) — be honest, even if they're vague]

Example:
"Write an FME Python script to pull Sentinel-2 imagery from Sentinel Hub for a
bounding box and save it as a GeoTIFF"

## Problems I've Encountered With Vibe-Coded Output
- [ ] Wrong coordinate reference system assumed
- [ ] Missing error handling for API rate limits
- [ ] Output file naming inconsistent
- [ ] Had to manually fix ______ before the script worked
- [ ] Script worked once but broke when ______ changed
- Other: ______

## How Many Iterations Did It Take to Get Usable Output?
[Number]

## Time Spent Debugging AI Output
[Estimate in minutes]
```

#### Step 1.2 — Capture the Actual Vibe-Coded Output

Run one more vibe-coded session right now, before you learn the new approach. This gives you a true A/B comparison:

```bash
# Start Claude Code in your working directory
cd ~/fme-spec-driven
claude

# Inside Claude Code, type your usual casual prompt:
# "Write a Python script for FME that [your workflow description]"
# Save the output as baseline_output.py
```

```bash
# Save Claude's output
cp /path/to/claude-output.py ~/fme-spec-driven/docs/baseline_output.py
```

Note in `baseline.md`:
- How many clarifying questions Claude asked (if any)
- How confident you feel the output is correct without testing
- What assumptions the output makes that you weren't explicit about

---

### Phase 2: Write the Formal Spec Document (45 minutes)

This is the core skill. A proper spec has seven components. We'll build each one.

#### Step 2.1 — Create Your Spec File

```bash
touch ~/fme-spec-driven/specs/workflow-spec-v1.md
```

#### Step 2.2 — Component 1: Workflow Identity

```markdown
# FME Workflow Specification

## Spec Metadata
- **Spec Version**: 1.0
- **Workflow Name**: [e.g., sentinel-hub-s2-pull]
- **Author**: [Your name]
- **Date**: [Today]
- **Status**: DRAFT | REVIEW | APPROVED
- **Replaces**: [baseline_output.py or "n/a"]

## Workflow Purpose
[One paragraph. What business problem does this solve? Who uses the output?
Be specific about the data domain — spatial data mistakes are expensive.]

Example:
"This workflow retrieves Sentinel-2 L2A surface reflectance imagery from the
Sentinel Hub Process API for a user-defined bounding box and time range,
reprojects to EPSG:4326, and exports to Cloud-Optimised GeoTIFF (COG) format
for ingestion into the project's Streamlit geospatial dashboard."
```

#### Step 2.3 — Component 2: Inputs Specification

This is where vibe-coding fails most often. Be exhaustive:

```markdown
## Inputs

### Required Inputs

| Parameter | Type | Format | Valid Range / Pattern | Example | Notes |
|---|---|---|---|---|---|
| `bbox` | Array[float] | [west, south, east, north] | Lat: -90 to 90, Lon: -180 to 180 | [14.2, 46.0, 14.8, 46.5] | WGS84 decimal degrees |
| `start_date` | String | ISO 8601 | Any valid past date | "2024-01-01" | Inclusive |
| `end_date` | String | ISO 8601 | >= start_date, <= today | "2024-03-31" | Inclusive |
| `instance_id` | String | UUID v4 | 36-char UUID | "abc123..." | From env var SENTINELHUB_INSTANCE_ID |
| `output_dir` | String | Absolute path | Must exist and be writable | "/data/sentinel/output" | Will NOT create directory |

### Optional Inputs

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `max_cloud_cover` | Float | 0.3 | Maximum cloud cover fraction (0.0–1.0) |
| `resolution_m` | Integer | 10 | Output resolution in metres (10, 20, or 60) |
| `bands` | Array[String] | ["B04","B03","B02","B08"] | Sentinel-2 band selection |

### Input Sources
- `instance_id`: Environment variable `SENTINELHUB_INSTANCE_ID` — NEVER hardcoded
- `bbox`, `start_date`, `end_date`: CLI arguments OR FME Published Parameters
- All other inputs: Config file at `./config/sentinel_defaults.json`

### Input Validation Rules
1. `bbox[0]` (west) MUST be < `bbox[2]` (east)
2. `bbox[1]` (south) MUST be < `bbox[3]` (north)
3. Bounding box area MUST NOT exceed 500 km² (API limit)
4. Date range MUST NOT exceed 365 days in a single call
5. `resolution_m` MUST be one of: 10, 20, 60
```

#### Step 2.4 — Component 3: Outputs Specification

```markdown
## Outputs

### Primary Output

| Output | Type | Format | Location | Naming Convention |
|---|---|---|---|---|
| Imagery file | Raster | Cloud-Optimised GeoTIFF | `{output_dir}/` | `s2_{start_date}_{end_date}_{west}_{south}.tif` |
| Run log | Text | JSON Lines | `{output_dir}/logs/` | `run_{timestamp}.jsonl` |

### Output File Requirements
- **CRS**: EPSG:4326 (WGS84 geographic)
- **Data type**: Float32
- **Nodata value**: -9999.0
- **Band order**: [B04=Red, B03=Green, B02=Blue, B08=NIR] when using defaults
- **COG compliance**: Must pass `rio cogeo validate` check
- **Metadata tags**: Must include `ACQUISITION_DATE`, `CLOUD_COVER`, `BBOX`, `SENTINELHUB_REQUEST_ID`

### Log Output Schema (JSON Lines)
Each line must be valid JSON matching:
```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARNING|ERROR",
  "event": "string",
  "details": {}
}
```

### Side Effects
- No modification of any input files
- No console output except errors (all info goes to log)
- No temporary files left on disk after successful completion
```

#### Step 2.5 — Component 4: Error Conditions

This section is what separates professional specs from amateur ones. Every error condition must be named, classified, and handled:

```markdown
## Error Conditions

### Error Classification

| Code | Name | Condition | Handling | Exit Code |
|---|---|---|---|---|
| E001 | INVALID_BBOX | bbox fails validation rules 1–3 | Log ERROR, raise ValueError with message, halt | 1 |
| E002 | INVALID_DATE_RANGE | Date range fails validation rules 4 | Log ERROR, raise ValueError, halt | 1 |
| E003 | MISSING_CREDENTIALS | SENTINELHUB_INSTANCE_ID not set | Log ERROR, raise EnvironmentError, halt | 2 |
| E004 | API_AUTH_FAILURE | 401/403 from Sentinel Hub | Log ERROR with status code, halt | 3 |
| E005 | API_RATE_LIMIT | 429 from Sentinel Hub | Log WARNING, retry with exponential backoff (3x max), then halt | 3 |
| E006 | API_TIMEOUT | Request exceeds 120s | Log WARNING, retry once, then log ERROR and halt | 3 |
| E007 | NO_DATA_FOUND | API returns 0 scenes for parameters | Log WARNING, write empty log entry, exit cleanly | 0 |
| E008 | OUTPUT_DIR_NOT_FOUND | `output_dir` does not exist | Log ERROR, halt — do NOT create directory silently | 1 |
| E009 | OUTPUT_WRITE_FAILURE | Cannot write to `output_dir` | Log ERROR with OS error message, halt | 4 |
| E010 | INVALID_RESOLUTION | `resolution_m` not in {10, 20, 60} | Log ERROR, halt | 1 |

### Retry Policy
- E005 (Rate Limit): Wait 2^n seconds where n = attempt number (2s, 4s, 8s)
- E006 (Timeout): Single retry after 30s delay
- All other errors: No retry — fail fast and loud

### What This Script Must NOT Do on Error
- Must NOT silently continue with partial/corrupt data
- Must NOT delete or overwrite existing output files on failure
- Must NOT catch all exceptions with a bare `except:` block
- Must NOT write a success log entry if any error occurred
```

#### Step 2.6 — Component 5: Acceptance Criteria

These are your pass/fail tests. Every criterion must be binary (pass or fail, not "looks good"):

```markdown
## Acceptance Criteria

### Functional Criteria (Must ALL pass)

**AC-01: Valid Input Produces Valid Output**
- GIVEN a valid bbox, date range, and credentials
- WHEN the script runs to completion
- THEN a GeoTIFF file exists at the expected output path
- AND the file passes `rio cogeo validate`
- AND the file CRS is EPSG:4326
- AND file metadata contains all four required tags

**AC-02: Invalid Bbox Is Rejected**
- GIVEN a bbox where west >= east
- WHEN the script is invoked
- THEN it exits with code 1
- AND logs an ERROR entry with code E001
- AND no output file is created

**AC-03: Missing Credentials Halts Cleanly**
- GIVEN SENTINELHUB_INSTANCE_ID is unset
- WHEN the script is invoked
- THEN it exits with code 2
- AND the error message explicitly names the missing variable

**AC-04: Rate Limit Triggers Retry**
- GIVEN the API returns 429 on first attempt
- WHEN the script handles the response
- THEN it retries up to 3 times with exponential backoff
- AND logs a WARNING (not ERROR) for each retry attempt

**AC-05: No Data Is Not an Error**
- GIVEN a valid request that returns 0 matching scenes
- WHEN the script completes
- THEN exit code is 0
- AND a log entry with event "NO_SCENES_FOUND" is written

**AC-06: Output Is Idempotent**
- GIVEN the script has already produced an output file
- WHEN the script is run again with identical parameters
- THEN the existing file is NOT overwritten (log WARNING, skip)
- OR a `--overwrite` flag must be explicitly passed

### Performance Criteria

**AC-07: Completion Time**
- A single-scene request for a 100km² AOI MUST complete within 300 seconds

### Code Quality Criteria

**AC-08: No Hardcoded Credentials**
- Static analysis (`grep -r "instance_id\s*=" *.py`) returns no matches on string literals

**AC-09: FME Integration Compatible**
- Script can be called from FME Python Caller transformer without modification
- All parameters accessible as FME Published Parameters

### Out of Scope (Explicitly)
- Multi-threaded downloads
- Mosaic of multiple scenes
- Automatic reprojection to non-WGS84 CRS
- GUI or interactive mode
```

#### Step 2.7 — Component 6: Technical Constraints

```markdown
## Technical Constraints

### Dependencies
```
sentinelhub>=3.9.0
rasterio>=1.3.0
click>=8.1.0
python-dotenv>=1.0.0
```

### FME Integration Requirements
- Compatible with FME 2022.x and later
- Must work as a Python Caller script (not standalone only)
- Published Parameters must use FME naming conventions (no hyphens)
- Must not require packages outside FME's bundled Python environment
  EXCEPT those listed above (to be installed in FME's Python env)

### Environment
- Target OS: Windows 10/11 and Ubuntu 22.04 LTS
- Python version: 3.9, 3.10, 3.11 (must work on all three)
- No async/await (FME Python Caller does not support asyncio)

### Security
- Credentials via environment variables only
- No credentials in config files, logs, or comments
- Log files must redact any UUID that could be an instance ID
```

#### Step 2.8 — Component 7: Test Data

```markdown
## Test Fixtures

### Valid Test Case (Happy Path)
```json
{
  "test_id": "TC-HAPPY-001",
  "bbox": [14.2, 46.0, 14.6, 46.3],
  "start_date": "2024-06-01",
  "end_date": "2024-06-30",
  "expected_exit_code": 0,
  "expected_output_exists": true,
  "notes": "Ljubljana area, summer 2024 — known clear scenes"
}
```

### Invalid BBox Test Case
```json
{
  "test_id": "TC-INVALID-BBOX-001",
  "bbox": [14.8, 46.0, 14.2, 46.3],
  "start_date": "2024-06-01",
  "end_date": "2024-06-30",
  "expected_exit_code": 1,
  "expected_output_exists": false,
  "expected_log_event": "E001"
}
```

### No Data Test Case
```json
{
  "test_id": "TC-NO-DATA-001",
  "bbox": [14.2, 46.0, 14.6, 46.3],
  "start_date": "2000-01-01",
  "end_date": "2000-01-02",
  "max_cloud_cover": 0.0,
  "expected_exit_code": 0,
  "expected_log_event": "NO_SCENES_FOUND"
}
```
```

---

### Phase 3: Drive Claude Code With the Spec (60–90 minutes)

Now the spec becomes your primary interface with Claude Code. You will reference it explicitly in every prompt.

#### Step 3.1 — Structure Your Claude Code Session

Create a project context file that Claude Code will use as its anchor:

```bash
# Create a CLAUDE.md file — Claude Code reads this automatically
cat > ~/fme-spec-driven/CLAUDE.md << 'EOF'
# Project Context for Claude Code

## What This Project Is
Spec-driven FME workflow automation. You are implementing against a formal specification.

## The Contract
- The specification in `specs/workflow-spec-v1.md` is the SOURCE OF TRUTH
- If the spec and my prompts conflict, ask me to clarify — do not assume
- If the spec is ambiguous, flag it before writing code
- Every function you write must be traceable to at least one acceptance criterion

## What You Must Not Do
- Do not add features not in the spec
- Do not use libraries not listed in the Technical Constraints section
- Do not hardcode any credentials, paths, or magic values
- Do not write bare `except:` clauses

## Code Style
- Type hints on all function signatures
- Docstrings on all public functions
- Error codes from the spec must appear as constants, not magic strings
- Log every state transition

## When You're Unsure
Ask. A question now is cheaper than a rework later.
EOF
```

#### Step 3.2 — Open Claude Code and Load the Spec

```bash
cd ~/fme-spec-driven
claude
```

Your first message to Claude Code establishes the contract. Do **not** skip this step:

```
/read specs/workflow-spec-v1.md
```

Then confirm Claude has understood it:

```
Before we write any code, summarise:
1. The three most complex error conditions from the spec
2. What AC-06 (idempotency) requires
3. Which dependencies are allowed

Do not start coding yet. Just confirm your understanding of the spec.
```

> **Why this matters**: This forces Claude to surface any ambiguities before they become bugs. If Claude's summary is wrong, your spec needs clarification — better to find that now.

#### Step 3.3 — Implement in Spec-Referenced Chunks

Never prompt "write the whole script." Implement component by component, always citing spec sections:

**Prompt 1: Constants and Error Codes**

```
Implement the error code constants from the Error Conditions table in the spec.
Create a file `scripts/sentinel_hub_pull.py` with:
- An ErrorCode enum or constants class with all E001-E010 codes
- The ExitCode mapping (e.g., exit code 1, 2, 3, 4)
- A structured logging setup that produces JSON Lines format as specified in the Outputs section

No business logic yet. Just the foundational types.
```

**Prompt 2: Input Validation**

```
Now implement the input validation layer.
Reference: Inputs section, Input Validation Rules 1-5, and error codes E001, E002, E008, E010.

Create a `validate_inputs()` function that:
- Accepts all parameters from the Required Inputs table
- Raises appropriate exceptions for each validation rule
- Each exception must include the error code as specified

Include unit-testable pure functions — no side effects in validation logic.

After writing, list which acceptance criteria (AC-XX) this implementation satisfies.
```

**Prompt 3: API Client Layer**

```
Implement the Sentinel Hub API client layer.
Reference: Technical Constraints (dependencies), Error Conditions E003-E007, and the retry policy.

Requirements:
- Use sentinelhub>=3.9.0 as specified
- Implement the retry logic exactly as specified in the Retry Policy section
- Credentials MUST come from environment variable only (see AC-08)
- Timeouts must match the 120s value in E006

Do not implement file I/O yet — return raw API response data only.
Annotate which error conditions each try/except block handles.
```

**Prompt 4: Output Writer**

```
Implement the output file writer.
Reference: Outputs section (Primary Output, Output File Requirements), error codes E009, and AC-06 (idempotency).

Requirements:
- Write COG-compliant GeoTIFF using rasterio as specified
- Apply exact metadata tags from the spec: ACQUISITION_DATE, CLOUD_COVER, BBOX, SENTINELHUB_REQUEST_ID
- Implement AC-06: if file exists and --overwrite not passed, log WARNING and skip
- Nodata value: -9999.0 as specified
- CRS: EPSG:4326 as specified

After writing, identify any spec requirement you could not implement and explain why.
```

**Prompt 5: Integration and CLI**

```
Now wire everything together into the main() function with a CLI.
Reference: Inputs section (Input Sources), Technical Constraints (click>=8.1.0), and AC-09 (FME compatibility).

Requirements:
- CLI parameters must match the Required and Optional Inputs tables exactly
- Parameter names must be FME-compatible (underscores, no hyphens in the Python variable names)
- Exit codes must match the Error Conditions table exactly
- The script must be importable without side effects (if __name__ == "__main__" guard)

Finally, generate the complete requirements list showing how each AC-01 through AC-09 is satisfied by specific functions or lines of code.
```

#### Step 3.4 — Handle Spec Gaps as They Emerge

During implementation, Claude will likely surface things your spec didn't cover. When this happens, **update the spec first, then continue**:

```
The spec doesn't specify what happens when Sentinel Hub returns a partial
result (some bands missing). Before you implement anything for this case,
I'm going to update the spec. Wait for my signal.

[Update specs/workflow-spec-v1.md with a new error code E011: PARTIAL_DATA]

Spec updated. Now implement the E011 handling as just specified.
```

This discipline — spec first, code second — is the core habit you're building.

#### Step 3.5 — Review the Complete Output

Once all components are written:

```
Review the complete implementation in scripts/sentinel_hub_pull.py against the spec.

Produce a compliance table:
| AC-ID | Criterion Summary | Implemented? | Location in Code | Notes |
|-------|-------------------|--------------|------------------|-------|

Flag any acceptance criteria that are NOT fully satisfied.
```

Save this table to your docs folder:

```bash
# Claude's compliance output → save it
# (copy/paste Claude's response)
cat > ~/fme-spec-driven/docs/compliance-table.md
```

---

### Phase 4: Validate the Implementation (30 minutes)

#### Step 4.1 — Run the Static Analysis Checks

```bash
cd ~/fme-spec-driven

# Check AC-08: No hardcoded credentials
grep -rn "instance_id\s*=" scripts/sentinel_hub_pull.py | grep -v "os.environ\|args\.\|param\.\|#"
# Expected: no output (zero matches)

# Check for bare except clauses (violates spec)
grep -n "except:" scripts/sentinel_hub_pull.py
# Expected: no output

# Check all error codes are defined
grep -n "E00[0-9]\|E010\|E011" scripts/sentinel_hub_pull.py
# Expected: each error code appears at least twice (definition + usage)
```

#### Step 4.2 — Run the Validation Test Suite

Create a validation script that tests each acceptance criterion:

```bash
cat > ~/fme-spec-driven/validation/run_acceptance_tests.sh << 'EOF'
#!/bin/bash
# Acceptance Test Runner — maps to spec AC-01 through AC-09

SCRIPT="python3 ../scripts/sentinel_hub_pull.py"
PASS=0
FAIL=0
SKIP=0

# Colour codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_result() {
    local test_id=$1
    local result=$2
    local detail=$3
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}[PASS]${NC} $test_id: $detail"
        ((PASS++))
    elif [ "$result" = "FAIL" ]; then
        echo -e "${RED}[FAIL]${NC} $test_id: $detail"
        ((FAIL++))
    else
        echo -e "${YELLOW}[SKIP]${NC} $test_id: $detail"
        ((SKIP++))
    fi
}

echo "=== FME Workflow Spec Acceptance Tests ==="
echo "Spec: workflow-spec-v1.md"
echo "Date: $(date)"
echo ""

# AC-02: Invalid BBox Rejected
echo "--- AC-02: Invalid BBox ---"
$SCRIPT --bbox "14.8,46.0,14.2,46.3" --start-date "2024-06-01" \
        --end-date "2024-06-30" --output-dir "/tmp/test_output" 2>/dev/null
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
    log_result "AC-02" "PASS" "Exit code 1 on invalid bbox"
else
    log_result "AC-02" "FAIL" "Expected exit 1, got $EXIT_CODE"
fi

# AC-03: Missing Credentials
echo "--- AC-03: Missing Credentials ---"
unset SENTINELHUB_INSTANCE_ID
$SCRIPT --bbox "14.2,46.0,14.6,46.3" --start-date "2024-06-01" \
        --end-date "2024-06-30" --output-dir "/tmp/test_output" 2>/dev/null
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    log_result "AC-03" "PASS" "Exit code 2 on missing credentials"
else
    log_result "AC-03" "FAIL" "Expected exit 2, got $EXIT_CODE"
fi

# AC-08: No Hardcoded Credentials
echo "--- AC-08: No Hardcoded Credentials ---"
MATCHES=$(grep -c 'instance_id\s*=\s*"' ../scripts/sentinel_hub_pull.py 2>/dev/null || echo "0")
if [ "$MATCHES" -eq 0 ]; then
    log_result "AC-08" "PASS" "No hardcoded credentials found"
else
    log_result "AC-08" "FAIL" "$MATCHES potential hardcoded credential(s) found"
fi

# AC-09: FME Importable
echo "--- AC-09: FME Import Compatible ---"
python3 -c "import sys; sys.path.insert(0, '../scripts'); import sentinel_hub_pull; print('import ok')" 2>/dev/null
if [ $? -eq 0 ]; then
    log_result "AC-09" "PASS" "Script importable without side effects"
else
    log_result "AC-09" "FAIL" "Script import raised exception"
fi

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed, ${SKIP} skipped ==="
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All testable acceptance criteria passed.${NC}"
    exit 0
else
    echo -e "${RED}${FAIL} acceptance criteria failed — do not ship.${NC}"
    exit 1
fi
EOF

chmod +x ~/fme-spec-driven/validation/run_acceptance_tests.sh
cd ~/fme-spec-driven/validation
./run_acceptance_tests.sh
```

#### Step 4.3 — Compare Against the Baseline

Now do the comparison you've been building toward:

```bash
cat > ~/fme-spec-driven/docs/comparison-report.md << 'EOF'
# Vibe-Coding vs. Spec-Driven: Comparison Report

## Workflow
[Workflow name]

## Date
[Today]

## Baseline (Vibe-Coded)

### Prompt Used
[Paste your original vague prompt]

### Output Quality
- [ ] Correct CRS handling? (Y/N)
- [ ] Error handling present? (Y/N)
- [ ] Credentials handled securely? (Y/N)
- [ ] Idempotency handled? (Y/N)
- [ ] FME-compatible? (tested)

### Issues Found During Review
1.
2.
3.

### Time to Usable Output
- Prompting: ___ minutes
- Debugging/fixing: ___ minutes
- Total: ___ minutes

### Acceptance Criteria Met (Against Spec)
X / 9 criteria met without modification

---

## Spec-Driven Output

### Spec Writing Time
___ minutes

### Claude Code Session Time
___ minutes

### Debugging Time
___ minutes

### Total Time
___ minutes

### Acceptance Criteria Met
X / 9 criteria met on first review

### Issues Found During Review
1. [Likely fewer]

---

## Delta Analysis

| Metric | Vibe-Coded | Spec-Driven | Delta |
|---|---|---|---|
| AC criteria met (first pass) | | | |
| Debug time (minutes) | | | |
| Total time to working output | | | |
| Error conditions handled | | | |
| Confidence in correctness (1–10) | | | |

## Qualitative Notes
[What surprised you? What spec gaps did you find during implementation?
What would you do differently next time?]

## Conclusion
[Is spec-driven worth the upfront investment for this workflow type?
Under what conditions would you NOT use it?]
EOF
```

Fill this in honestly. The delta analysis is your Build column entry.

---

### Phase 5: Extract the Reusable Template (15 minutes)

#### Step 5.1 — Create a Blank Spec Template

```bash
cat > ~/fme-spec-driven/specs/TEMPLATE-