# Test the everything-claude-code Harness on a Real GIS Scripting Task

## A Hands-On Tool Critic Tutorial

---

## 1. Introduction & Context

### What This Is

This tutorial walks you through cloning the **everything-claude-code** harness — a structured layer on top of Claude Code CLI that adds persistent memory, skills definitions, security patterns, and research-first development workflows — and stress-testing it against a real-world **GIS scripting task** using Python, GeoPandas, and Rasterio.

The end product is a published **Tool Critic piece**: a structured evaluation of whether the harness measurably reduces prompt iteration cycles compared to vanilla Claude Code usage.

### Why It Matters

Claude Code CLI is a powerful agentic coding tool, but without scaffolding it suffers from:

- **Context amnesia** — every session forgets prior decisions
- **Security drift** — no enforced guardrails on file writes, API calls, or shell execution
- **Prompt thrash** — users re-explain domain context repeatedly
- **No orchestration layer** — multi-step workflows require manual chaining

The `everything-claude-code` harness from [affaan-m](https://github.com/affaan-m/everything-claude-code) addresses all four with:

| Layer | What It Adds |
|---|---|
| **Skills** | Reusable capability definitions the agent can invoke |
| **Memory** | Persistent context files the agent reads on startup |
| **Security** | Explicit permission scopes and operation sandboxing |
| **Research-First** | Structured discovery phase before any code generation |

### The GIS Task We'll Use

We'll use a representative real-world task:

> **"Clip a raster DEM to a study area polygon, compute zonal statistics per watershed, and export a CSV summary + styled map PNG."**

This task is ideal for benchmarking because it has:
- Clear inputs/outputs (measurable correctness)
- Domain-specific terminology the agent must understand
- Multi-step workflow requiring coordination
- File I/O and shell commands (where security patterns matter)

---

## 2. Prerequisites

### Knowledge

- [ ] Basic Python (functions, file I/O, virtual environments)
- [ ] Passing familiarity with GIS concepts (rasters, vectors, projections)
- [ ] Comfort with CLI/terminal usage
- [ ] Basic understanding of what Claude Code CLI does (you don't need to be an expert)

### Software

```bash
# Check these are available before starting
python --version        # 3.10+ recommended
git --version           # any modern version
node --version          # 18+ (required by Claude Code CLI)
npm --version           # comes with node
```

### Accounts & API Keys

- [ ] **Anthropic API key** with Claude Sonnet or Opus access — get one at [console.anthropic.com](https://console.anthropic.com)
- [ ] GitHub account (for publishing your Tool Critic piece)

### Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # verify installation
```

### Python GIS Environment

```bash
# Create a dedicated environment (conda recommended for GIS)
conda create -n gis-harness python=3.11 -y
conda activate gis-harness

# Install GIS stack — conda handles the tricky binary dependencies
conda install -c conda-forge geopandas rasterio rasterstats matplotlib fiona pyproj shapely -y

# Verify
python -c "import geopandas, rasterio, rasterstats; print('GIS stack OK')"
```

> **Alternative with pip (Linux/Mac):**
> ```bash
> pip install geopandas rasterio rasterstats matplotlib pyproj shapely
> ```

---

## 3. Step-by-Step Guide

### Phase 0: Establish Your Measurement Framework (10 minutes)

Before touching any code, set up your evaluation scorecard. This is what separates a Tool Critic piece from a casual blog post.

Create your benchmarking journal:

```bash
mkdir -p ~/tool-critic/gis-harness-test
cd ~/tool-critic/gis-harness-test
touch benchmark_log.md
```

Paste this template into `benchmark_log.md`:

```markdown
# Harness Benchmark Log

## Baseline Session (Vanilla Claude Code)
- Date:
- Task: Clip DEM → zonal stats → CSV + PNG
- Prompts to working solution: ___
- Prompts wasted on re-explaining context: ___
- Security incidents (unintended writes/deletes): ___
- Time to first runnable code (minutes): ___
- Final code quality (1–5): ___

## Harness Session (everything-claude-code)
- Date:
- Task: (same task)
- Prompts to working solution: ___
- Prompts wasted on re-explaining context: ___
- Security incidents: ___
- Time to first runnable code (minutes): ___
- Final code quality (1–5): ___

## Delta Analysis
- Prompt reduction: ___%
- Time savings: ___ minutes
- Qualitative differences:
```

---

### Phase 1: Baseline Run — Vanilla Claude Code (20 minutes)

Run the GIS task *without* the harness first. This gives you the control condition.

#### 1.1 Set Your API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

#### 1.2 Create the Baseline Project

```bash
mkdir -p ~/tool-critic/baseline-gis
cd ~/tool-critic/baseline-gis
```

#### 1.3 Download Sample GIS Data

```bash
# We'll use SRTM elevation data (public domain) and a watershed polygon
# This script downloads test data for the exercise
python3 << 'EOF'
import urllib.request
import os

os.makedirs("data", exist_ok=True)

# Download a small SRTM tile (30m DEM) via OpenTopography-style URL
# Using a small sample from USGS for the tutorial
print("Downloading sample DEM (this may take a moment)...")

# Use a synthetic DEM if download is slow — uncomment to generate locally:
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

# Generate a synthetic 100x100 DEM for the tutorial
data = np.random.randint(200, 3000, (100, 100), dtype=np.int16)
data = np.where(data > 2500, data, data)  # add some elevation variation

transform = from_bounds(-122.5, 37.5, -122.0, 38.0, 100, 100)
crs = CRS.from_epsg(4326)

with rasterio.open(
    "data/dem.tif",
    "w",
    driver="GTiff",
    height=100,
    width=100,
    count=1,
    dtype=data.dtype,
    crs=crs,
    transform=transform,
) as dst:
    dst.write(data, 1)

print("Created data/dem.tif (synthetic 100x100 DEM)")

# Create sample watershed polygons
import geopandas as gpd
from shapely.geometry import box, Polygon
import pandas as pd

watersheds = gpd.GeoDataFrame(
    {
        "watershed_id": [1, 2, 3],
        "name": ["North Fork", "South Fork", "Main Stem"],
        "area_km2": [45.2, 38.7, 62.1],
        "geometry": [
            box(-122.45, 37.6, -122.25, 37.8),
            box(-122.45, 37.5, -122.25, 37.6),
            box(-122.25, 37.5, -122.0, 37.9),
        ],
    },
    crs="EPSG:4326",
)
watersheds.to_file("data/watersheds.gpkg", driver="GPKG")
print("Created data/watersheds.gpkg (3 watershed polygons)")
print("\nData ready. Files in ./data/")
EOF
```

#### 1.4 Start Vanilla Claude Code Session

```bash
cd ~/tool-critic/baseline-gis
claude
```

Now enter these prompts **one at a time**, logging how many it takes to reach working code:

**Prompt 1 (Baseline):**
```
I have a GIS project with a DEM raster at data/dem.tif and watershed polygons at 
data/watersheds.gpkg. Write a Python script that:
1. Clips the DEM to each watershed polygon
2. Computes zonal statistics (min, max, mean, std elevation) per watershed
3. Exports results to output/zonal_stats.csv
4. Creates a styled map PNG at output/watershed_map.png showing the DEM with 
   watershed boundaries overlaid and labeled
Use geopandas, rasterio, rasterstats, and matplotlib.
```

> 📋 **Log:** Record what Claude Code returns. Does it ask clarifying questions? Does it make assumptions? Does it get the imports right? Does it handle CRS mismatches?

**Continue prompting** until you have working code. Count every exchange. Note when you had to re-explain what GeoPandas is, what a watershed is, or what CRS means.

#### 1.5 Run the Baseline Code

```bash
mkdir -p output
python gis_analysis.py  # or whatever Claude named it
```

Fix any errors, counting each fix as an additional prompt cycle.

#### 1.6 Record Baseline Metrics

Fill in the **Baseline Session** section of your `benchmark_log.md` now, while it's fresh.

---

### Phase 2: Clone and Configure the everything-claude-code Harness (15 minutes)

#### 2.1 Clone the Repository

```bash
cd ~/tool-critic
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
ls -la  # Survey the structure
```

Take 5 minutes to read the README and understand the directory structure before proceeding.

#### 2.2 Understand the Harness Architecture

```bash
# Typical structure you'll find (explore and map it out):
find . -name "*.md" -o -name "*.json" -o -name "*.yaml" | head -30
```

Key components to identify:

```
everything-claude-code/
├── CLAUDE.md              # ← Master directive file (agent reads this first)
├── skills/                # ← Reusable capability definitions
│   ├── coding.md
│   ├── research.md
│   └── ...
├── memory/                # ← Persistent context the agent carries forward
│   ├── project_context.md
│   └── ...
├── security/              # ← Permission scopes and guardrails
│   └── permissions.md
└── patterns/              # ← Orchestration templates
    └── ...
```

> **Note:** The exact structure may evolve as the repo is updated. Adapt the paths below to match what you actually find.

#### 2.3 Set Up Your Harness-Backed GIS Project

```bash
mkdir -p ~/tool-critic/harness-gis
cd ~/tool-critic/harness-gis

# Copy your same test data
cp -r ~/tool-critic/baseline-gis/data ./data
mkdir -p output
```

#### 2.4 Initialize the Harness in Your Project

The core of this setup is creating a `CLAUDE.md` file that gives the agent persistent context. This is where the harness earns its keep.

```bash
# Copy the harness CLAUDE.md as your starting template
cp ~/tool-critic/everything-claude-code/CLAUDE.md ./CLAUDE.md
```

Now **edit** `CLAUDE.md` to add your GIS project context. Open it and append a new section:

```bash
cat >> CLAUDE.md << 'EOF'

---

## Project: GIS Watershed Analysis Harness

### Domain Context
This project performs terrain analysis on DEM raster data using watershed polygon boundaries.
- **DEM**: `data/dem.tif` — GeoTIFF, EPSG:4326, integer Int16 elevation values in meters
- **Watersheds**: `data/watersheds.gpkg` — GeoPackage, EPSG:4326, fields: watershed_id, name, area_km2
- **Output dir**: `output/` — all generated files go here

### GIS Stack
- `geopandas` — vector data (polygons, attribute joins)
- `rasterio` — raster I/O and clipping
- `rasterstats` — zonal statistics (always use `zonal_stats()` from this library)
- `matplotlib` + `contextily` — mapping and basemap tiles

### Critical GIS Rules (always follow these)
1. ALWAYS check and align CRS before any spatial operation: `assert gdf.crs == raster_crs`
2. Use `all_touched=True` in rasterstats for small polygons
3. Handle nodata values explicitly: `nodata=-9999` or read from raster metadata
4. Reproject to a projected CRS (e.g., EPSG:32610) before area/distance calculations
5. Never hardcode bounding boxes — derive from data geometry

### Security Scope
- READ: `data/` directory (rasters and vectors)
- WRITE: `output/` directory only
- FORBIDDEN: Any writes to `data/`, system paths, or network calls without explicit approval

### Memory: Previous Decisions
- Synthetic DEM generated at 100x100 pixels, bounds: -122.5 to -122.0 lon, 37.5 to 38.0 lat
- Watershed polygons: 3 features (North Fork, South Fork, Main Stem)
- Chosen visualization: terrain colormap (cmap='terrain') with viridis-compatible colorbar
EOF
```

#### 2.5 Copy Skills Definitions

```bash
# Copy relevant skill files from the harness
mkdir -p skills
cp ~/tool-critic/everything-claude-code/skills/*.md ./skills/ 2>/dev/null || echo "Skills dir structure may differ — check repo"

# If skills are structured differently, manually create a GIS skill:
cat > skills/gis_analysis.md << 'EOF'
# Skill: GIS Raster-Vector Analysis

## Capability
Clip rasters to polygon features, compute zonal statistics, and produce publication-quality maps.

## Standard Workflow
1. **Load and validate** — read files, check CRS alignment, print basic metadata
2. **Reproject if needed** — align all layers to a single CRS before analysis  
3. **Clip** — use rasterio.mask.mask() for raster clipping to polygon extent
4. **Zonal stats** — use rasterstats.zonal_stats() with nodata handling
5. **Join** — merge stats back to GeoDataFrame via watershed_id
6. **Export** — CSV with pandas, PNG with matplotlib (dpi=150 minimum)

## Error Patterns to Avoid
- Forgetting to pass `nodata` value to zonal_stats → inflated mean values
- Using lat/lon CRS for rasterio clip operations → incorrect extents  
- Not closing rasterio datasets → file lock issues on Windows
- Hardcoding figure size for rasters of unknown dimensions

## Quality Gates
- [ ] All spatial joins produce expected row count
- [ ] CSV contains no NaN values in stat columns
- [ ] PNG has legend, title, north arrow placeholder, and scale reference
- [ ] Script runs end-to-end with `python script.py` without errors
EOF
```

#### 2.6 Configure Security Permissions

```bash
cat > security/permissions.md << 'EOF'
# Security Permissions: GIS Watershed Project

## Allowed Operations
| Operation | Scope | Requires Confirmation |
|-----------|-------|----------------------|
| File Read | `data/` only | No |
| File Write | `output/` only | No |
| File Delete | NONE | Always block |
| Shell Exec | `python`, `pip list` | No |
| Network | NONE | Always block |
| System Paths | NONE | Always block |

## Enforcement
- Before any write operation, confirm path starts with `output/`
- Before any delete operation, STOP and ask user
- If asked to overwrite source data, REFUSE and explain why
EOF
```

---

### Phase 3: Run the Harness Session (25 minutes)

#### 3.1 Start Claude Code with Harness Context

```bash
cd ~/tool-critic/harness-gis
claude
```

#### 3.2 The Harness Prompt Battery

Now run the **same task** but observe how the harness changes the interaction quality. Start with a deliberately brief prompt to test whether the persistent context compensates:

**Prompt 1 (Harness — intentionally minimal):**
```
Run the full watershed analysis pipeline per our project setup.
```

> 📋 **Observe:** Does the agent correctly reference `data/dem.tif` and `data/watersheds.gpkg` without being told? Does it follow the GIS rules in CLAUDE.md? Does it use `rasterstats` correctly?

**Prompt 2 (if needed — test memory):**
```
Add the security validation you know about before any file write.
```

> 📋 **Observe:** Does it pull the security scope from `security/permissions.md`?

**Prompt 3 (test skill invocation):**
```
Apply the GIS analysis quality gates from our skills before finalizing.
```

> 📋 **Observe:** Does it reference `skills/gis_analysis.md`?

#### 3.3 Run the Harness-Generated Code

```bash
mkdir -p output
python gis_analysis.py
```

Compare outputs:

```bash
# Both runs should produce these files
ls ~/tool-critic/baseline-gis/output/
ls ~/tool-critic/harness-gis/output/

# Quick diff of the generated scripts
diff ~/tool-critic/baseline-gis/gis_analysis.py \
     ~/tool-critic/harness-gis/gis_analysis.py
```

#### 3.4 Complete Reference Implementation

If Claude Code's output has issues, here's a complete reference implementation to compare against. This is what a high-quality output should look like:

```python
#!/usr/bin/env python3
"""
Watershed Elevation Analysis
Clips DEM to watershed polygons, computes zonal statistics,
exports CSV summary and styled map PNG.
"""

import os
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
from matplotlib.colors import LightSource

# ─── Configuration ──────────────────────────────────────────────────────────

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
DEM_PATH = DATA_DIR / "dem.tif"
WATERSHEDS_PATH = DATA_DIR / "watersheds.gpkg"
CSV_OUTPUT = OUTPUT_DIR / "zonal_stats.csv"
MAP_OUTPUT = OUTPUT_DIR / "watershed_map.png"

STATS = ["min", "max", "mean", "std", "count"]
NODATA_VALUE = -9999


# ─── Security Validation ─────────────────────────────────────────────────────

def validate_write_path(path: Path) -> None:
    """Enforce that all writes stay within OUTPUT_DIR."""
    path = Path(path).resolve()
    output_resolved = OUTPUT_DIR.resolve()
    if not str(path).startswith(str(output_resolved)):
        raise PermissionError(
            f"SECURITY: Attempted write outside output dir: {path}"
        )


# ─── Data Loading & Validation ───────────────────────────────────────────────

def load_and_validate_data():
    """Load raster and vector data, validate CRS alignment."""
    print("Loading data...")

    # Load watersheds
    watersheds = gpd.read_file(WATERSHEDS_PATH)
    print(f"  Watersheds: {len(watersheds)} features, CRS={watersheds.crs}")

    # Load raster metadata
    with rasterio.open(DEM_PATH) as src:
        raster_crs = src.crs
        raster_bounds = src.bounds
        raster_nodata = src.nodata or NODATA_VALUE
        print(f"  DEM: {src.width}x{src.height} px, CRS={raster_crs}")
        print(f"  DEM bounds: {raster_bounds}")
        print(f"  DEM nodata: {raster_nodata}")

    # CRS alignment check
    if watersheds.crs != raster_crs:
        print(f"  CRS mismatch — reprojecting watersheds to {raster_crs}")
        watersheds = watersheds.to_crs(raster_crs)

    return watersheds, raster_nodata


# ─── Zonal Statistics ────────────────────────────────────────────────────────

def compute_zonal_statistics(watersheds: gpd.GeoDataFrame, nodata: float) -> gpd.GeoDataFrame:
    """Compute elevation statistics per watershed polygon."""
    print("\nComputing zonal statistics...")

    # rasterstats expects GeoJSON-like geometries
    geometries = [feature.__geo_interface__ for feature in watersheds.geometry]

    stats = zonal_stats(
        geometries,
        str(DEM_PATH),
        stats=STATS,
        nodata=nodata,
        all_touched=True,  # include cells touched by boundary
        geojson_out=False,
    )

    # Convert to DataFrame and join back
    stats_df = pd.DataFrame(stats)
    stats_df.columns = [f"elev_{col}" for col in stats_df.columns]

    result = watersheds.copy()
    for col in stats_df.columns:
        result[col] = stats_df[col].values

    # Quality gate: no NaN in stat columns
    stat_cols = [c for c in result.columns if c.startswith("elev_")]
    nan_counts = result[stat_cols].isna().sum()
    if nan_counts.any():
        print(f"  WARNING: NaN values found in stats:\n{nan_counts[nan_counts > 0]}")
    else:
        print("  Quality gate passed: no NaN values in elevation stats")

    print(result[["name"] + stat_cols].to_string(index=False))
    return result


# ─── Export CSV ──────────────────────────────────────────────────────────────

def export_csv(result: gpd.GeoDataFrame) -> None:
    """Export zonal statistics to CSV (no geometry column)."""
    validate_write_path(CSV_OUTPUT)
    OUTPUT_DIR.mkdir(exist_ok=True)

    export_cols = [c for c in result.columns if c != "geometry"]
    df = result[export_cols].copy()

    # Round float columns for readability
    float_cols = df.select_dtypes(include="float").columns
    df[float_cols] = df[float_cols].round(2)

    df.to_csv(CSV_OUTPUT, index=False)
    print(f"\nCSV exported: {CSV_OUTPUT}")
    print(f"  Rows: {len(df)}, Columns: {list(df.columns)}")


# ─── Styled Map ──────────────────────────────────────────────────────────────

def create_styled_map(watersheds: gpd.GeoDataFrame) -> None:
    """Create styled map PNG with DEM background and watershed overlays."""
    validate_write_path(MAP_OUTPUT)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\nGenerating styled map...")

    with rasterio.open(DEM_PATH) as src:
        dem_data = src.read(1).astype(float)
        nodata = src.nodata or NODATA_VALUE
        dem_data[dem_data == nodata] = np.nan
        extent = [src.bounds.left, src.bounds.right,
                  src.bounds.bottom, src.bounds.top]

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Plot DEM with terrain colormap
    im = ax.imshow(
        dem_data,
        extent=extent,
        cmap="terrain",
        origin="upper",
        alpha=0.85,
        vmin=np.nanpercentile(dem_data, 2),
        vmax=np.nanpercentile(dem_data, 98),
    )

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Elevation (m)", fontsize=10)

    # Watershed boundaries with labels
    colors = ["#E74C3C", "#3498DB", "#2ECC71"]
    for idx, (_, row) in enumerate(watersheds.iterrows()):
        color = colors[idx % len(colors)]
        gpd.GeoDataFrame([row], crs=watersheds.crs).plot(
            ax=ax,
            facecolor="none",
            edgecolor=color,
            linewidth=2.5,
            linestyle="--",
        )
        # Label at centroid
        centroid = row.geometry.centroid
        ax.annotate(
            row["name"],
            xy=(centroid.x, centroid.y),
            fontsize=8,
            fontweight="bold",
            color=color,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
        )

    # Legend patches
    patches = [
        mpatches.Patch(edgecolor=colors[i], facecolor="none",
                       linestyle="--", linewidth=2, label=row["name"])
        for i, (_, row) in enumerate(watersheds.iterrows())
    ]
    ax.legend(handles=patches, loc="lower right", fontsize=9,
              framealpha=0.85, title="Watersheds")

    # Titles and labels
    ax.set_title("Watershed Elevation Analysis\n(Synthetic DEM — Tutorial Dataset)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)
    ax.tick_params(labelsize=8)

    # Minimal "north arrow" annotation
    ax.annotate("N ↑", xy=(0.02, 0.95), xycoords="axes fraction",
                fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(MAP_OUTPUT, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Map exported: {MAP_OUTPUT} (150 dpi)")


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Watershed Elevation Analysis Pipeline")
    print("=" * 55)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Step 1: Load and validate
    watersheds, nodata = load_and_validate_data()

    # Step 2: Zonal statistics
    result = compute_zonal_statistics(watersheds, nodata)

    # Step 3: Export CSV
    export_csv(result)

    # Step 4: Styled map
    create_styled_map(watersheds)

    print("\n" + "=" * 55)
    print("  Pipeline complete.")
    print(f"  → {CSV_OUTPUT}")
    print(f"  → {MAP_OUTPUT}")
    print("=" * 55)


if __name__ == "__main__":
    main()
```

Save this as `reference_implementation.py` and run it to confirm your environment is healthy:

```bash
cd ~/tool-critic/harness-gis
python reference_implementation.py
```

---

### Phase 4: Measure and Compare (15 minutes)

#### 4.1 Code Quality Comparison Script

```python
# save as compare_outputs.py
"""Quick comparison of baseline vs harness outputs."""
import hashlib
import os
from pathlib import Path


def file_stats(path):
    if not Path(path).exists():
        return {"exists": False}
    text = Path(path).read_text(errors="ignore")
    return {
        "exists": True,
        "lines": text.count("\n"),
        "chars": len(text),
        "has_nodata_handling": "nodata" in text.lower(),
        "has_crs_check": "crs" in text.lower(),
        "has_security_check": "output" in text.lower() and ("validate" in text or "permission" in text.lower()),
        "has_docstrings": '"""' in text or "'''" in text,
        "has_type_hints": ": " in text and "->" in text,
        "has_error_handling": "try:" in text or "except" in text,
    }


baseline = file_stats("../baseline-gis/gis_analysis.py")
harness = file_stats("gis_analysis.py")

print("=" * 50)
print("Code Quality Comparison")
print("=" * 50)
print(f"{'Attribute':<30} {'Baseline':>10} {'Harness':>10}")
print("-" * 50)
for key in baseline:
    b_val = str(baseline.get(key, "N/A"))
    h_val = str(harness.get(key, "N/A"))
    flag = "✓" if h_val == "True" and b_val == "False" else " "
    print(f"{flag} {key:<28} {b_val:>10} {h_val:>10}")
```

```bash
cd ~/tool-critic/harness-gis
python compare_outputs.py
```

#### 4.2 Output Correctness Check

```python
# save as validate_outputs.py
"""Validate that both pipeline outputs are correct."""
import pandas as pd
from pathlib import Path

for session in ["baseline-gis", "harness-gis"]:
    csv_path = Path(f"../{session}/output/zonal_stats.csv")
    print(f"\n--- {session} ---")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Has NaN: {df.isna().any().any()}")
        elev_cols = [c for c in df.columns if "elev" in c]
        if elev_cols:
            print(f"  Stats cols: {elev_cols}")
            print(df[elev_cols].describe().round(1).to_string())
    else:
        print(f"  MISSING: {csv_path}")

    png_path = Path(f"../{session}/output/watershed_map.png")
    print(f"  Map PNG exists: {png_path.exists()}")
    if png_path.exists():
        size_kb = png_path.stat().st_size / 1024
        print(f"  Map PNG size: {size_kb:.1f} KB")
```

```bash
python validate_outputs.py
```

---

### Phase 5: Write the Tool Critic Piece (30 minutes)

#### 5.1 Tool Critic Template

Create your evaluation write-up using this structure:

```bash
cat > ~/tool-critic/tool_critic_piece.md << 'TEMPLATE'
# Tool Critic: everything-claude-code on a Real GIS Task

**Tested by:** [Your Name]  
**Date:** [Date]  
**Repo tested:** https://github.com/affaan-m/everything-claude-code  
**Task:** Clip DEM raster → zonal watershed statistics → CSV + styled map PNG  
**Environment:** Python 3.11, GeoPandas, Rasterio, Rasterstats  

---

## TL;DR

[2–3 sentence summary: Did the harness reduce prompt iteration? By how much? Would you use it?]

---

## What I Tested

### Task Description
[Describe the GIS task in plain language]

### Setup Time
- Cloning and configuring the harness: ___ minutes
- Configuring CLAUDE.md for the GIS domain: ___ minutes
- Writing skills and security files: ___ minutes

---

## Benchmark Results

| Metric | Baseline (Vanilla) | Harness | Delta |
|--------|----------------