# AI Discovery Hub: Content Pipeline & Lab Routing

This document details the complete chain of thought and technical pipeline for how the AI Discovery Hub fetches, filters, and curates content. It traces the journey of a single piece of content from the internet all the way to becoming an actionable exercise in "The Lab".

## Phase 1: Ingestion & Pre-Filtering (`fetch_feed.py`)

The pipeline begins with a deterministic data gathering script that pulls from three primary sources. Content is heavily pre-filtered before it ever reaches the LLM to save tokens and ensure a high baseline of signal.

1.  **YouTube (API v3)**:
    *   **Selection**: Scans a hardcoded list of highly relevant channels (e.g., Fireship, Andrej Karpathy, Safe Software) AND a list of specific search queries (e.g., "Claude Code AI agent", "FME Safe Software automation").
    *   **Filtering**: Only pulls videos published within the specified lookback window (default 7 days). Caps the total volume (default 10 videos) after deduplicating URLs and sorting by recency.
2.  **GitHub (REST API)**:
    *   **Selection**: Searches repositories matching specific technical topics critical to the stack (e.g., `llm`, `ai-agent`, `mcp-server`, `fme`, `geoai`).
    *   **Filtering**: Enforces a strict heuristic of `stars:>10` and `pushed:>[since_date]` to ignore abandoned or low-traction repositories. Caps total repos (default 15) sorted by star count.
3.  **Reddit (Public JSON Endpoints)**:
    *   **Selection**: Scrapes the "hot" feeds of specific subreddits (`r/MachineLearning`, `r/LocalLLaMA`, `r/gis`, etc.).
    *   **Filtering**: Ignores any post with a score `< 50`, ignores stickied mod posts, and ignores posts older than the lookback window. Caps total posts (default 10) sorted by score.

**Output of Phase 1**: A consolidated JSON file (`data/hub-input.json`) containing a raw mix of high-signal videos, repos, and social signals.

---

## Phase 2: LLM Curation & Classification (`prompts.py` & `build_hub.py`)

The raw JSON is injected into a massive context prompt sent to an LLM (defaulting to Claude 3.5 Sonnet). The prompt acts as an orchestrator, scoring and classifying the content based on a strict set of rules, a defined `STACK_PROFILE`, and a `USER_CONTEXT`.

### How It Knows What to Ignore (The "World" Filter)
The LLM evaluates every item against the `STACK_PROFILE`. 
*   **The "Personal" Stack**: Items that use Python, React, Vite, Claude API, or GIS tools (FME, QGIS, Sentinel Hub) are marked as `personal`.
*   **The "Adjacent" Rule**: If an item isn't in the direct stack but is a 1-step upgrade or replacement (e.g., a new frontend framework challenging React, or an alternative to FME), it is also kept as `personal`.
*   **The Rejection List**: The prompt contains an explicit `NOT RELEVANT` list. This includes mobile development (iOS/Android), languages like Java/Rust/C++, gaming engines, and Web3/Crypto. 
*   **The "Ignore" Mechanism**: Instead of completely deleting irrelevant items, the LLM sets their relevance to `world`. In the dashboard UI, `world` items are stripped of context, relegated to the bottom "AI World at Large" section, and explicitly excluded from all analytics, tiers, and Lab exercises. They are retained strictly for situational awareness.

### How Content is Scored for the Board
For all items that survive as `personal`, the LLM assigns them a specific Lens and Tier:
*   **Lens**: Categorizes the context of the item (e.g., `🏠 Home Hobbyist`, `📡 Staying Current`, `🗺 GIS/FME`).
*   **Tiering (Priority Matrix)**:
    *   `✅ Adopt Now`: High ROI, ready to use immediately.
    *   `👁 Watch Closely`: Important signal, needs evaluation.
    *   `🔥 Hype Check`: Viral but needs verification.
    *   `🏗 Foundation`: Core infrastructure to learn.
    *   `🌱 On Radar`: Early traction, not yet proven.

---

## Phase 3: "The Lab" Exercise Generation

"The Lab" is the actionable core of the dashboard, designed to move content from "passive reading" to "active implementation." The LLM generates the Lab exercises dynamically during the generation pass in `build_hub.py`.

The routing into the Lab works via a strict rule defined in `prompts.py`:
1.  **The "Adopt Now" Trigger**: EVERY single artifact that the LLM classified as `✅ Adopt Now` **MUST** have a corresponding exercise generated for it. This is a one-to-one mapping enforced by the system prompt.
2.  **The Fallback**: If there are fewer than 3 items deemed "Adopt Now" in a given week, the LLM is instructed to dip into the `👁 Watch Closely` tier and generate exploratory exercises for those items until there are at least 3 items in the Lab.
3.  **Exercise Structuring**: The LLM creates an actionable JSON object for each exercise containing:
    *   A title.
    *   An effort level (`low`, `med`, `high`).
    *   A description of exactly what to test, build, or integrate based on the artifact.
    *   A reference link back to the source artifact.

**Final Output**: The LLM returns a structured JSON payload which `build_hub.py` parses and injects into a static HTML template, grouping the content logically and rendering the final dashboard.
