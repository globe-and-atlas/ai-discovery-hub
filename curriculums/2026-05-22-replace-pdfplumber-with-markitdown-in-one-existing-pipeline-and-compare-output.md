# Replace `pdfplumber` with `markitdown` in One Existing Pipeline and Compare Output

## 1. Introduction & Context

### What This Is

This tutorial walks you through swapping `markitdown` — Microsoft's open-source Markdown conversion library — into an existing PDF parsing pipeline that currently uses `pdfplumber`. The goal is concrete and measurable: run both parsers on the same GIS technical document, compare the output quality side-by-side, and determine whether `markitdown`'s structured Markdown output improves the quality of prompts you send to the Claude API.

### Why It's Worth Your Time

Your current `pdfplumber` workflow extracts raw text that you then need to clean, structure, and format before passing to Claude. `markitdown` outputs Markdown directly — headings, tables, lists, and links are preserved as semantic structure rather than raw character streams. LLMs including Claude are trained on vast amounts of Markdown and understand it natively, which means:

- **Less prompt engineering** to explain document structure
- **More token-efficient** context windows (Markdown markup is minimal)
- **Better table handling** — critical for FME release notes, Sentinel Hub parameter tables, and coordinate reference system documentation
- **Broader format coverage** as a free side-effect: Word, Excel, PowerPoint, and HTML all work with the same `convert()` call

This is a low-effort, high-signal exercise. You have the existing script. You swap one dependency. You measure the difference.

---

## 2. Prerequisites

### Software

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | `markitdown` hard requirement |
| pip | Current | Or `uv` if you prefer |
| Existing `pdfplumber` script | Any | Your GIS/FME/Sentinel Hub parser |
| A target PDF | Any | FME release notes, Sentinel Hub docs, or similar |
| Anthropic SDK | Current | `pip install anthropic` |

### Knowledge

- You have a working `pdfplumber` script that extracts text from a PDF and passes it to Claude
- You are comfortable running Python scripts from the command line
- You have an Anthropic API key set in your environment

### Verify Your Python Version

```bash
python --version
# Must output 3.10 or higher
```

---

## 3. Step-by-Step Guide

### Step 1: Set Up a Clean Virtual Environment

Create an isolated environment so this swap doesn't disturb your existing `pdfplumber` project.

```bash
# Using standard Python venv
python -m venv .venv-markitdown
source .venv-markitdown/bin/activate
```

Or with `uv` (faster):

```bash
uv venv --python=3.12 .venv-markitdown
source .venv-markitdown/bin/activate
```

### Step 2: Install `markitdown` with PDF Support

Install with all optional dependencies to ensure PDF parsing works out of the box:

```bash
pip install 'markitdown[all]'
```

If you want a minimal install scoped only to PDF (and optionally Word/PowerPoint for future use):

```bash
pip install 'markitdown[pdf,docx,pptx]'
```

Also install the Anthropic SDK if not already present:

```bash
pip install anthropic
```

### Step 3: Capture Your Baseline `pdfplumber` Output

Before touching anything, run your existing script and save its output to a file. This is your baseline for comparison.

> **Note:** The script below is a representative example of a typical `pdfplumber` → Claude pipeline. Adapt the function names and variable structure to match your own existing script.

```python
# baseline_pdfplumber.py
# Run this FIRST, before any changes, to capture your baseline output.

import pdfplumber
import json

PDF_PATH = "fme_release_notes.pdf"          # ← swap in your actual PDF path
OUTPUT_PATH = "baseline_pdfplumber_raw.txt"

def extract_with_pdfplumber(pdf_path: str) -> str:
    """Your existing extraction logic — adapt to match your actual script."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text.append(f"--- Page {page_num} ---\n{text}")
    return "\n\n".join(full_text)


def build_claude_prompt(extracted_text: str) -> str:
    """Your existing prompt builder — adapt to match your actual script."""
    return f"""You are a GIS technical analyst. The following text was extracted from a PDF document.
Please summarise the key changes, features, or parameters described.

DOCUMENT TEXT:
{extracted_text}

SUMMARY:"""


if __name__ == "__main__":
    raw_text = extract_with_pdfplumber(PDF_PATH)

    # Save raw extraction for comparison
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)

    print(f"✅ pdfplumber extraction saved to {OUTPUT_PATH}")
    print(f"   Characters extracted: {len(raw_text):,}")
    print(f"   Lines extracted:      {raw_text.count(chr(10)):,}")

    # Save the prompt itself
    prompt = build_claude_prompt(raw_text)
    with open("baseline_pdfplumber_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print("   Prompt saved to baseline_pdfplumber_prompt.txt")
```

Run it:

```bash
python baseline_pdfplumber.py
```

### Step 4: Run the CLI Smoke Test with `markitdown`

Before writing any Python, verify `markitdown` is installed correctly and can parse your PDF at the command line:

```bash
markitdown fme_release_notes.pdf -o markitdown_output.md
```

Open `markitdown_output.md` in any text editor and do a quick visual scan. You should immediately see:

- `#` and `##` headings where pdfplumber gave you plain uppercase text
- `|` pipe-delimited tables where pdfplumber gave you space-aligned columns
- `-` bullet lists where pdfplumber gave you `•` or `–` characters

If the file is empty or throws an error, check that the `[pdf]` optional dependency was installed:

```bash
pip show pdfminer.six   # This is the backend markitdown[pdf] installs
```

### Step 5: Build the `markitdown` Equivalent Script

Now create the replacement script. The key change is the extraction function — the Claude API call stays identical so the comparison is fair.

```python
# markitdown_pipeline.py
# Direct replacement for your pdfplumber extraction script.

from markitdown import MarkItDown
import anthropic
import os

PDF_PATH = "fme_release_notes.pdf"          # ← same PDF as Step 3
MARKDOWN_OUTPUT_PATH = "markitdown_output.md"

# ── Extraction ─────────────────────────────────────────────────────────────

def extract_with_markitdown(pdf_path: str) -> str:
    """
    Replace your pdfplumber extraction block with this single call.
    MarkItDown returns a result object; .text_content holds the Markdown string.
    """
    md = MarkItDown()
    result = md.convert(pdf_path)
    return result.text_content


# ── Prompt Builder ──────────────────────────────────────────────────────────

def build_claude_prompt(markdown_text: str) -> str:
    """
    Same prompt structure as your baseline — but now the document content
    is already structured Markdown rather than raw extracted text.
    """
    return f"""You are a GIS technical analyst. The following document has been converted to Markdown.
Please summarise the key changes, features, or parameters described.

DOCUMENT MARKDOWN:
{markdown_text}

SUMMARY:"""


# ── Claude API Call ─────────────────────────────────────────────────────────

def call_claude(prompt: str) -> str:
    """
    Identical Claude API call to your baseline — change nothing here
    so the only variable is the input text quality.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Extract
    markdown_text = extract_with_markitdown(PDF_PATH)

    # 2. Save Markdown output for comparison
    with open(MARKDOWN_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    print(f"✅ markitdown extraction saved to {MARKDOWN_OUTPUT_PATH}")
    print(f"   Characters extracted: {len(markdown_text):,}")
    print(f"   Lines extracted:      {markdown_text.count(chr(10)):,}")

    # 3. Build prompt and save for comparison
    prompt = build_claude_prompt(markdown_text)
    with open("markitdown_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print("   Prompt saved to markitdown_prompt.txt")

    # 4. Call Claude and save response
    print("\n⏳ Calling Claude API...")
    response = call_claude(prompt)
    with open("markitdown_claude_response.txt", "w", encoding="utf-8") as f:
        f.write(response)

    print("✅ Claude response saved to markitdown_claude_response.txt")
    print("\n── Claude Summary ─────────────────────────────────────────────")
    print(response)
```

Run it:

```bash
python markitdown_pipeline.py
```

### Step 6: Build a Side-by-Side Comparison Script

This script quantifies the difference between the two extractions so your comparison is objective, not just vibes.

```python
# compare_outputs.py
# Produces a structured before/after report you can include in your build notes.

import re

def load(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def count_tables(text: str) -> int:
    """Count Markdown pipe-table rows (lines containing |...|)."""
    return sum(1 for line in text.splitlines() if re.match(r"^\s*\|.+\|", line))


def count_headings(text: str) -> int:
    """Count Markdown headings (lines starting with #)."""
    return sum(1 for line in text.splitlines() if re.match(r"^#{1,6} ", line))


def count_list_items(text: str) -> int:
    """Count Markdown bullet/numbered list items."""
    return sum(1 for line in text.splitlines() if re.match(r"^\s*[-*+] ", line) or
               re.match(r"^\s*\d+\. ", line))


def report(label: str, text: str) -> dict:
    return {
        "label": label,
        "characters": len(text),
        "lines": text.count("\n"),
        "headings": count_headings(text),
        "table_rows": count_tables(text),
        "list_items": count_list_items(text),
    }


if __name__ == "__main__":
    pdfplumber_text = load("baseline_pdfplumber_raw.txt")
    markitdown_text = load("markitdown_output.md")

    results = [
        report("pdfplumber (baseline)", pdfplumber_text),
        report("markitdown (new)",      markitdown_text),
    ]

    print("\n┌─────────────────────────────────────────────────────────────┐")
    print("│           PDF EXTRACTION COMPARISON REPORT                  │")
    print("├─────────────────────┬──────────────────┬────────────────────┤")
    print(f"│ {'Metric':<19} │ {'pdfplumber':>16} │ {'markitdown':>18} │")
    print("├─────────────────────┼──────────────────┼────────────────────┤")

    metrics = ["characters", "lines", "headings", "table_rows", "list_items"]
    labels  = ["Characters", "Lines", "Headings (#)", "Table rows", "List items"]

    for metric, label in zip(metrics, labels):
        a = results[0][metric]
        b = results[1][metric]
        delta = f"(+{b-a})" if b > a else f"({b-a})" if b < a else "(=)"
        print(f"│ {label:<19} │ {a:>16,} │ {b:>14,} {delta:>3} │")

    print("└─────────────────────┴──────────────────┴────────────────────┘")
    print()

    # Highlight structural wins
    h_diff = results[1]["headings"]   - results[0]["headings"]
    t_diff = results[1]["table_rows"] - results[0]["table_rows"]
    l_diff = results[1]["list_items"] - results[0]["list_items"]

    if h_diff > 0:
        print(f"✅ markitdown recovered {h_diff} heading(s) that pdfplumber missed")
    if t_diff > 0:
        print(f"✅ markitdown recovered {t_diff} table row(s) as structured Markdown")
    if l_diff > 0:
        print(f"✅ markitdown recovered {l_diff} list item(s) as structured Markdown")
    if h_diff == 0 and t_diff == 0 and l_diff == 0:
        print("⚠️  No structural difference detected — this PDF may be image-based.")
        print("   Consider the markitdown-ocr plugin (see Next Steps).")
```

Run it:

```bash
python compare_outputs.py
```

### Step 7: Also Run the Baseline Claude Call for Direct Response Comparison

> **Note:** If your existing `pdfplumber` script already calls Claude, you can skip this step and reuse that saved response. If not, run this minimal version to get a comparable Claude response from the pdfplumber text.

```python
# baseline_claude_call.py
import anthropic
import os

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

raw_text = load("baseline_pdfplumber_raw.txt")

prompt = f"""You are a GIS technical analyst. The following text was extracted from a PDF document.
Please summarise the key changes, features, or parameters described.

DOCUMENT TEXT:
{raw_text}

SUMMARY:"""

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
response_text = message.content[0].text

with open("baseline_pdfplumber_claude_response.txt", "w", encoding="utf-8") as f:
    f.write(response_text)

print("── pdfplumber → Claude Response ───────────────────────────────")
print(response_text)
```

---

## 4. Validation

### Checklist: Did the Exercise Work?

Run through each item. All six should be true before you call this complete.

```
[ ] markitdown_output.md exists and is non-empty
[ ] compare_outputs.py runs without errors and prints a table
[ ] headings count is higher in markitdown output than pdfplumber output
[ ] table_rows count is higher in markitdown output (if the PDF has tables)
[ ] markitdown_claude_response.txt contains a coherent summary
[ ] The markitdown Claude summary mentions specific section names or
    table values that the pdfplumber summary missed or mangled
```

### What Good Output Looks Like

**`pdfplumber` raw extraction (typical):**
```
COORDINATE REFERENCE SYSTEMS
Supported CRS
EPSG 4326 WGS 84 geographic   Yes
EPSG 32633 UTM Zone 33N       Yes
EPSG 3857 Web Mercator        Partial
```

**`markitdown` Markdown output (typical):**
```markdown
## Coordinate Reference Systems

### Supported CRS

| EPSG Code | Name                  | Supported |
|-----------|-----------------------|-----------|
| 4326      | WGS 84 geographic     | Yes       |
| 32633     | UTM Zone 33N          | Yes       |
| 3857      | Web Mercator          | Partial   |
```

The Markdown version gives Claude unambiguous column relationships — it no longer has to infer that `Partial` belongs to the `3857` row rather than floating in space after a line break.

### Manual Quality Check: Three Specific Things to Verify

Open both output files side by side and check these three locations:

1. **Document title / first heading** — Does `markitdown` render it as `# Title` rather than all-caps plain text?
2. **First table in the document** — Does `markitdown` produce pipe syntax? Can you read which value belongs to which column?
3. **Any bulleted list** — Does `markitdown` use `- item` syntax rather than `• item` or `– item` with inconsistent spacing?

If all three are yes: `markitdown` is producing meaningfully better input for Claude.

---

## 5. Next Steps

### Immediate: Make the Swap Permanent

Once you're satisfied with the comparison, replace the `pdfplumber` extraction block in your production script. The change is typically **three lines**:

```python
# BEFORE
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

# AFTER
from markitdown import MarkItDown
md = MarkItDown()
text = md.convert(pdf_path).text_content
```

### If Your PDF is Scanned / Image-Based

If `compare_outputs.py` showed no structural improvement (zero headings, zero tables), your PDF is likely scanned rather than born-digital. Use the `markitdown-ocr` plugin with an LLM vision backend:

```bash
pip install markitdown-ocr
pip install openai
```

```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o",
)
result = md.convert("scanned_document.pdf")
print(result.text_content)
```

> **Note:** This requires an OpenAI API key and will incur costs proportional to the number of pages. The source documentation states that if no `llm_client` is provided the plugin loads but OCR is silently skipped.

### Expand to Other Document Types

Your `markitdown` install already supports formats you likely encounter in a GIS workflow — no additional code changes needed:

```python
md = MarkItDown()

# FME workbench documentation (Word)
result = md.convert("fme_workspace_notes.docx")

# Sentinel Hub parameter tables (Excel)
result = md.convert("band_combinations.xlsx")

# Conference slides (PowerPoint)
result = md.convert("esri_uc_presentation.pptx")

# All produce result.text_content as Markdown
```

### Refine Your Claude Prompt for Markdown Input

Now that Claude is receiving structured Markdown, update your system prompt to explicitly leverage it:

```python
system_prompt = """You are a GIS technical analyst.
The user will provide document content in Markdown format.
Use the heading hierarchy to understand document structure.
Reference table column headers explicitly when citing values.
Use the same section headings in your response that appear in the source document."""
```

### Candidate Metrics for Your Build Notes

Record these before/after values for your write-up:

| Metric | pdfplumber | markitdown |
|---|---|---|
| Headings detected | `_` | `_` |
| Table rows structured | `_` | `_` |
| Claude response accuracy* | `_` | `_` |
| Prompt tokens used | `_` | `_` |

*Accuracy = number of specific facts in the Claude response that are verifiably correct when checked against the source PDF.