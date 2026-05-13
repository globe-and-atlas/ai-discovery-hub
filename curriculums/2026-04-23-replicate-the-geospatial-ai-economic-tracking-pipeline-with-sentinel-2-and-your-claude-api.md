# Replicate the Geospatial AI Economic Tracking Pipeline with Sentinel-2 and Claude API

## A Hands-On Tutorial for Building a Satellite-Powered Economic Intelligence System

---

## 1. Introduction & Context

### What Is This?

This tutorial walks you through building a **minimal but production-representative geospatial AI pipeline** that mirrors the approach demonstrated in the Wisdom Hill video. The goal is to pull real satellite imagery of a port or logistics site, extract meaningful spectral and spatial features, and feed that data to Claude Sonnet to generate a structured economic activity summary — all in Python.

Think of it as a "junior analyst in a box": the pipeline watches a location from orbit and uses AI to translate raw pixels into economic intelligence.

### Why Is This Worth Learning?

- **Real-world signal extraction**: Governments, hedge funds, and logistics firms pay millions for this capability. You're building a free-tier version from scratch.
- **Full-stack geospatial AI**: You'll touch APIs, raster processing, vector analysis, and LLM prompting in a single cohesive workflow.
- **Transferable architecture**: The port-tracking pipeline you build here is structurally identical to pipelines monitoring crop health, construction activity, retail parking lots, or industrial output.
- **The "Build" pillar in practice**: This is exactly the kind of artifact that demonstrates technical depth for Globe & Atlas's Industry Lens editorial angle.

### What You'll Build

```
Sentinel Hub API → Raw Sentinel-2 GeoTIFF → rasterio/geopandas processing
       → Derived indices (NDVI, NDWI, brightness) + metadata
              → Claude Sonnet API (structured prompt)
                     → JSON economic activity summary
```

### Target Use Case

We'll track a **single container port** (Rotterdam, Port of Los Angeles, or a port of your choice) using a defined bounding box. The pipeline will assess vessel density proxies, waterfront activity, and infrastructure brightness changes as economic signals.

---

## 2. Prerequisites

### Knowledge Requirements

| Skill | Level Needed |
|---|---|
| Python | Intermediate (functions, classes, file I/O) |
| REST APIs | Basic (you've made GET/POST requests before) |
| Geospatial concepts | Beginner-friendly (terms explained inline) |
| Command line | Basic (cd, pip, environment variables) |

### Accounts and API Keys

Before writing a single line of code, gather the following:

1. **Sentinel Hub account** (free tier available)
   - Sign up at [https://www.sentinel-hub.com](https://www.sentinel-hub.com)
   - Create an OAuth client under *User Settings → OAuth clients*
   - Note your `CLIENT_ID` and `CLIENT_SECRET`

2. **Anthropic API key**
   - Obtain at [https://console.anthropic.com](https://console.anthropic.com)
   - Note your `ANTHROPIC_API_KEY`

3. **Optional: Copernicus Data Space account** (free alternative for imagery)
   - [https://dataspace.copernicus.eu](https://dataspace.copernicus.eu)

### Local Environment Requirements

```bash
# Python 3.10+ recommended
python --version

# Required system libraries (Ubuntu/Debian)
sudo apt-get install libgdal-dev gdal-bin

# macOS with Homebrew
brew install gdal
```

### Python Packages

Create a dedicated virtual environment:

```bash
python -m venv geospatial-ai-env
source geospatial-ai-env/bin/activate  # Windows: geospatial-ai-env\Scripts\activate

pip install \
  sentinelhub \
  rasterio \
  geopandas \
  numpy \
  matplotlib \
  anthropic \
  python-dotenv \
  shapely \
  pyproj \
  requests \
  Pillow
```

### Project Structure

Set up your working directory now:

```bash
mkdir geospatial-ai-pipeline
cd geospatial-ai-pipeline
mkdir -p data/raw data/processed outputs notebooks

touch .env pipeline.py sentinel_client.py raster_processor.py claude_analyst.py main.py
```

Your `.env` file:

```env
SENTINEL_CLIENT_ID=your_client_id_here
SENTINEL_CLIENT_SECRET=your_client_secret_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

> ⚠️ **Security note**: Add `.env` to your `.gitignore` immediately. Never commit API keys.

---

## 3. Step-by-Step Guide

### Step 1: Define Your Area of Interest (AOI)

We'll use the **Port of Rotterdam** as our reference site. It's large, well-documented, and frequently imaged. You can swap this bounding box for any port worldwide.

Create a file called `config.py`:

```python
# config.py
# Area of Interest: Port of Rotterdam (Maasvlakte terminal area)
# Coordinates are in WGS84 (EPSG:4326): [min_lon, min_lat, max_lon, max_lat]

AOI_CONFIG = {
    "name": "Port of Rotterdam - Maasvlakte",
    "bbox": [4.00, 51.93, 4.15, 52.02],  # [west, south, east, north]
    "epsg": 4326,
    "description": "Europe's largest port, primary container and bulk cargo hub"
}

# Date range for imagery search (adjust to recent dates for best results)
DATE_CONFIG = {
    "start_date": "2024-10-01",
    "end_date": "2024-11-30",
    "max_cloud_cover": 20  # percent - reject cloudy scenes
}

# Sentinel-2 bands to download
# B02=Blue, B03=Green, B04=Red, B08=NIR, B11=SWIR1
BANDS_CONFIG = {
    "bands": ["B02", "B03", "B04", "B08", "B11"],
    "resolution": 20  # meters per pixel (10 or 20 available)
}
```

**Understanding the bounding box**: The four numbers define a rectangle on the Earth's surface. Think of it as drawing a box on a map — west edge, south edge, east edge, north edge. You can find coordinates for any location using [bboxfinder.com](http://bboxfinder.com).

---

### Step 2: Authenticate and Query Sentinel Hub

Create `sentinel_client.py`:

```python
# sentinel_client.py
"""
Handles all Sentinel Hub API interactions:
- Authentication
- Scene discovery (finding available images)
- Image download
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    bbox_to_dimensions,
    SentinelHubCatalog,
    filter_times,
)
import numpy as np

load_dotenv()


def get_sentinel_config() -> SHConfig:
    """Build and validate Sentinel Hub configuration from environment variables."""
    config = SHConfig()
    config.sh_client_id = os.getenv("SENTINEL_CLIENT_ID")
    config.sh_client_secret = os.getenv("SENTINEL_CLIENT_SECRET")

    if not config.sh_client_id or not config.sh_client_secret:
        raise ValueError(
            "Missing Sentinel Hub credentials. "
            "Check SENTINEL_CLIENT_ID and SENTINEL_CLIENT_SECRET in .env"
        )

    return config


def search_available_scenes(
    bbox_coords: list,
    start_date: str,
    end_date: str,
    max_cloud_cover: int = 20,
    config: SHConfig = None
) -> list:
    """
    Query Sentinel Hub catalog for available Sentinel-2 scenes.

    Args:
        bbox_coords: [west, south, east, north] in WGS84
        start_date: ISO format date string "YYYY-MM-DD"
        end_date: ISO format date string "YYYY-MM-DD"
        max_cloud_cover: Maximum acceptable cloud cover percentage
        config: Authenticated SHConfig object

    Returns:
        List of scene metadata dictionaries, sorted by date
    """
    if config is None:
        config = get_sentinel_config()

    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    catalog = SentinelHubCatalog(config=config)

    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,  # Level-2A = atmospherically corrected (surface reflectance)
        bbox=bbox,
        time=(start_date, end_date),
        filter=f"eo:cloud_cover < {max_cloud_cover}",
        fields={
            "include": [
                "id",
                "properties.datetime",
                "properties.eo:cloud_cover",
                "properties.s2:mgrs_tile",
                "properties.platform"
            ]
        }
    )

    scenes = []
    for item in search_iterator:
        scenes.append({
            "scene_id": item["id"],
            "datetime": item["properties"]["datetime"],
            "cloud_cover": item["properties"].get("eo:cloud_cover", 0),
            "tile": item["properties"].get("s2:mgrs_tile", "unknown"),
            "platform": item["properties"].get("platform", "sentinel-2")
        })

    # Sort by date, most recent first
    scenes.sort(key=lambda x: x["datetime"], reverse=True)

    print(f"Found {len(scenes)} scenes between {start_date} and {end_date}")
    for scene in scenes[:5]:  # Show top 5
        print(f"  {scene['datetime'][:10]} | Cloud: {scene['cloud_cover']:.1f}% | Tile: {scene['tile']}")

    return scenes


def download_sentinel2_scene(
    bbox_coords: list,
    acquisition_date: str,
    bands: list,
    resolution: int = 20,
    output_dir: str = "data/raw",
    config: SHConfig = None
) -> dict:
    """
    Download a Sentinel-2 multispectral scene for the given AOI.

    Args:
        bbox_coords: [west, south, east, north] in WGS84
        acquisition_date: Target date "YYYY-MM-DD" (will use ±3 day window)
        bands: List of band names e.g. ["B02", "B03", "B04", "B08", "B11"]
        resolution: Spatial resolution in meters (10 or 20)
        output_dir: Directory to save downloaded files
        config: Authenticated SHConfig object

    Returns:
        Dictionary with file paths and scene metadata
    """
    if config is None:
        config = get_sentinel_config()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

    # Calculate image dimensions based on bounding box and resolution
    size = bbox_to_dimensions(bbox, resolution=resolution)
    print(f"Image dimensions: {size[0]} x {size[1]} pixels at {resolution}m resolution")

    # Build the evalscript — this is the JavaScript-like code Sentinel Hub executes
    # to select and process bands before delivery
    band_list = ", ".join([f"B.{b}" for b in bands])
    evalscript = f"""
    //VERSION=3
    function setup() {{
        return {{
            input: [{{
                bands: {json.dumps(bands)},
                units: "REFLECTANCE"
            }}],
            output: {{
                bands: {len(bands)},
                sampleType: "FLOAT32"
            }}
        }};
    }}

    function evaluatePixel(sample) {{
        return [{", ".join([f"sample.{b}" for b in bands])}];
    }}
    """

    # Define the time window (3 days either side of target date)
    from datetime import timedelta
    target = datetime.strptime(acquisition_date, "%Y-%m-%d")
    time_interval = (
        (target - timedelta(days=3)).strftime("%Y-%m-%d"),
        (target + timedelta(days=3)).strftime("%Y-%m-%d")
    )

    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order="leastCC",  # least cloud cover mosaic
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        bbox=bbox,
        size=size,
        config=config,
        data_folder=output_dir,
    )

    print(f"Downloading Sentinel-2 scene for {acquisition_date}...")
    data = request.get_data(save_data=True)

    # The library saves files in a hash-named subdirectory
    # Find the most recently created .tiff file
    output_path = Path(output_dir)
    tiff_files = list(output_path.rglob("*.tiff")) + list(output_path.rglob("*.tif"))

    if not tiff_files:
        raise FileNotFoundError("No TIFF file found after download. Check Sentinel Hub credentials and quota.")

    latest_tiff = max(tiff_files, key=lambda f: f.stat().st_mtime)

    result = {
        "tiff_path": str(latest_tiff),
        "bands": bands,
        "bbox": bbox_coords,
        "acquisition_date": acquisition_date,
        "resolution_m": resolution,
        "image_size_px": size,
        "data_array": data[0] if data else None
    }

    print(f"✓ Downloaded: {latest_tiff}")
    print(f"  Array shape: {data[0].shape if data else 'N/A'}")

    return result
```

**What's happening here**: Sentinel Hub's API works by sending an *evalscript* (a small JavaScript snippet) that tells their cloud infrastructure which bands to extract and how to process them before sending you the pixels. You're essentially running code against petabytes of archived imagery without downloading the raw files yourself.

---

### Step 3: Process the Raster Data with rasterio

Create `raster_processor.py`:

```python
# raster_processor.py
"""
Raster and vector processing module.
Computes spectral indices and spatial statistics that serve as
economic activity proxies.
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import geopandas as gpd
from shapely.geometry import box, mapping
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


def load_raster_data(tiff_path: str, bands: list) -> dict:
    """
    Load a multi-band GeoTIFF into numpy arrays.

    Args:
        tiff_path: Path to the downloaded GeoTIFF
        bands: Ordered list of band names matching the file's band order

    Returns:
        Dictionary mapping band names to 2D numpy arrays
    """
    with rasterio.open(tiff_path) as src:
        metadata = {
            "width": src.width,
            "height": src.height,
            "crs": str(src.crs),
            "transform": src.transform,
            "bounds": src.bounds,
            "count": src.count,
            "dtype": src.dtypes[0],
            "nodata": src.nodata
        }

        band_arrays = {}
        for i, band_name in enumerate(bands, start=1):
            if i <= src.count:
                arr = src.read(i).astype(np.float32)
                # Mask no-data values
                if src.nodata is not None:
                    arr = np.where(arr == src.nodata, np.nan, arr)
                band_arrays[band_name] = arr
            else:
                print(f"Warning: Band {band_name} (index {i}) not found in file")

    print(f"✓ Loaded raster: {metadata['width']}×{metadata['height']} px, {len(band_arrays)} bands")
    return {"bands": band_arrays, "metadata": metadata}


def compute_spectral_indices(band_arrays: dict) -> dict:
    """
    Compute spectral indices used as economic activity proxies.

    Economic interpretation:
    - NDVI (vegetation): Low NDVI over expected green areas → land use change, construction
    - NDWI (water): High NDWI in port basins → water presence; changes → vessel density proxy
    - Brightness (visible): High brightness → bare ground, concrete, vessel hulls
    - SWIR ratio: Identifies built environment vs. natural surfaces

    Bands required:
        B02 = Blue (490nm)
        B03 = Green (560nm)
        B04 = Red (665nm)
        B08 = NIR (842nm)
        B11 = SWIR1 (1610nm)
    """
    indices = {}
    available = set(band_arrays.keys())

    # NDVI: Normalized Difference Vegetation Index
    # Range: -1 to 1. High values = dense vegetation. Low/negative = water, built environment
    if {"B08", "B04"}.issubset(available):
        nir = band_arrays["B08"]
        red = band_arrays["B04"]
        with np.errstate(divide="ignore", invalid="ignore"):
            ndvi = np.where(
                (nir + red) != 0,
                (nir - red) / (nir + red),
                np.nan
            )
        indices["NDVI"] = ndvi
        print(f"  NDVI: mean={np.nanmean(ndvi):.3f}, std={np.nanstd(ndvi):.3f}")

    # NDWI: Normalized Difference Water Index (McFeeters 1996)
    # Range: -1 to 1. Positive values = open water. Used to detect vessels/water bodies
    if {"B03", "B08"}.issubset(available):
        green = band_arrays["B03"]
        nir = band_arrays["B08"]
        with np.errstate(divide="ignore", invalid="ignore"):
            ndwi = np.where(
                (green + nir) != 0,
                (green - nir) / (green + nir),
                np.nan
            )
        indices["NDWI"] = ndwi
        print(f"  NDWI: mean={np.nanmean(ndwi):.3f}, std={np.nanstd(ndwi):.3f}")

    # MNDWI: Modified NDWI using SWIR (better for ports with industrial water)
    if {"B03", "B11"}.issubset(available):
        green = band_arrays["B03"]
        swir = band_arrays["B11"]
        with np.errstate(divide="ignore", invalid="ignore"):
            mndwi = np.where(
                (green + swir) != 0,
                (green - swir) / (green + swir),
                np.nan
            )
        indices["MNDWI"] = mndwi
        print(f"  MNDWI: mean={np.nanmean(mndwi):.3f}, std={np.nanstd(mndwi):.3f}")

    # Brightness: Average of visible bands
    # High brightness in port areas → vessel hulls, containers, active quays
    visible_bands = [b for b in ["B02", "B03", "B04"] if b in available]
    if visible_bands:
        visible_stack = np.stack([band_arrays[b] for b in visible_bands], axis=0)
        brightness = np.nanmean(visible_stack, axis=0)
        indices["brightness"] = brightness
        print(f"  Brightness: mean={np.nanmean(brightness):.4f}, std={np.nanstd(brightness):.4f}")

    # NDBI: Normalized Difference Built-up Index
    # Positive values = built environment (concrete, metal roofing, pavement)
    if {"B11", "B08"}.issubset(available):
        swir = band_arrays["B11"]
        nir = band_arrays["B08"]
        with np.errstate(divide="ignore", invalid="ignore"):
            ndbi = np.where(
                (swir + nir) != 0,
                (swir - nir) / (swir + nir),
                np.nan
            )
        indices["NDBI"] = ndbi
        print(f"  NDBI: mean={np.nanmean(ndbi):.3f}, std={np.nanstd(ndbi):.3f}")

    return indices


def compute_scene_statistics(band_arrays: dict, indices: dict, bbox: list) -> dict:
    """
    Aggregate raster data into scene-level statistics suitable for LLM consumption.

    Args:
        band_arrays: Dictionary of band name → 2D array
        indices: Dictionary of index name → 2D array
        bbox: [west, south, east, north] bounding box

    Returns:
        Flat dictionary of scalar statistics
    """
    stats = {}

    # Spatial coverage info
    west, south, east, north = bbox
    lat_center = (north + south) / 2
    lon_center = (east + west) / 2
    area_approx_km2 = (
        abs(east - west) * 111.32 * np.cos(np.radians(lat_center))
    ) * (abs(north - south) * 110.574)

    stats["spatial"] = {
        "bbox_wgs84": bbox,
        "center_lat": round(lat_center, 4),
        "center_lon": round(lon_center, 4),
        "approx_area_km2": round(area_approx_km2, 2)
    }

    # Per-index statistics
    index_stats = {}
    for index_name, array in indices.items():
        valid = array[~np.isnan(array)]
        if len(valid) > 0:
            percentiles = np.percentile(valid, [5, 25, 50, 75, 95])
            index_stats[index_name] = {
                "mean": round(float(np.mean(valid)), 4),
                "std": round(float(np.std(valid)), 4),
                "min": round(float(np.min(valid)), 4),
                "max": round(float(np.max(valid)), 4),
                "p5": round(float(percentiles[0]), 4),
                "p25": round(float(percentiles[1]), 4),
                "median": round(float(percentiles[2]), 4),
                "p75": round(float(percentiles[3]), 4),
                "p95": round(float(percentiles[4]), 4),
                "valid_pixel_fraction": round(float(len(valid) / array.size), 3)
            }

    stats["spectral_indices"] = index_stats

    # Land cover fractions (rough classification)
    if "NDVI" in indices and "NDWI" in indices:
        ndvi = indices["NDVI"]
        ndwi = indices["NDWI"]
        total_valid = np.sum(~np.isnan(ndvi))

        if total_valid > 0:
            water_fraction = np.sum(ndwi > 0.1) / total_valid
            vegetation_fraction = np.sum(ndvi > 0.3) / total_valid
            built_fraction = np.sum((ndvi < 0.1) & (ndwi < 0.0)) / total_valid

            stats["land_cover_fractions"] = {
                "water_approx": round(float(water_fraction), 3),
                "vegetation_approx": round(float(vegetation_fraction), 3),
                "built_bare_approx": round(float(built_fraction), 3),
            }

    # High-brightness zone analysis (proxy for vessel/container density)
    if "brightness" in indices:
        brightness = indices["brightness"]
        valid_brightness = brightness[~np.isnan(brightness)]
        if len(valid_brightness) > 0:
            bright_threshold = np.percentile(valid_brightness, 80)
            very_bright_threshold = np.percentile(valid_brightness, 95)

            stats["brightness_zones"] = {
                "top_20pct_threshold": round(float(bright_threshold), 4),
                "top_5pct_threshold": round(float(very_bright_threshold), 4),
                "top_20pct_pixel_count": int(np.sum(brightness > bright_threshold)),
                "top_5pct_pixel_count": int(np.sum(brightness > very_bright_threshold)),
                "mean_brightness": round(float(np.nanmean(brightness)), 4)
            }

    return stats


def create_rgb_preview(band_arrays: dict, output_path: str = "outputs/preview_rgb.png"):
    """
    Generate a true-color RGB preview image for visual validation.

    Args:
        band_arrays: Dictionary of band arrays (needs B04, B03, B02)
        output_path: Where to save the PNG
    """
    from PIL import Image

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    required = ["B04", "B03", "B02"]
    if not all(b in band_arrays for b in required):
        print(f"Cannot create RGB preview: need {required}, have {list(band_arrays.keys())}")
        return

    # Stack R, G, B bands
    rgb = np.stack([band_arrays["B04"], band_arrays["B03"], band_arrays["B02"]], axis=2)

    # Percentile stretch for visualization (standard remote sensing approach)
    for i in range(3):
        channel = rgb[:, :, i]
        valid = channel[~np.isnan(channel)]
        if len(valid) > 0:
            p2, p98 = np.percentile(valid, [2, 98])
            rgb[:, :, i] = np.clip((channel - p2) / (p98 - p2 + 1e-8), 0, 1)

    # Replace NaN with 0
    rgb = np.nan_to_num(rgb, nan=0.0)

    # Convert to uint8
    rgb_uint8 = (rgb * 255).astype(np.uint8)

    img = Image.fromarray(rgb_uint8)
    img.save(output_path)
    print(f"✓ RGB preview saved: {output_path}")

    return output_path
```

---

### Step 4: Build the Claude Analyst Module

This is where the magic happens. Create `claude_analyst.py`:

```python
# claude_analyst.py
"""
Claude Sonnet integration for economic intelligence extraction.

Design philosophy:
- We pass STATISTICS, not images, to Claude
- The model reasons about economic meaning from spectral/spatial features
- Output is structured JSON for downstream use
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()


def build_economic_analysis_prompt(
    scene_stats: dict,
    site_config: dict,
    acquisition_date: str,
    historical_context: str = None
) -> str:
    """
    Construct a detailed prompt for economic activity analysis.

    The prompt follows a "expert persona + structured data + specific output format" pattern
    that consistently produces high-quality structured responses from Claude.
    """

    stats_json = json.dumps(scene_stats, indent=2)

    historical_section = ""
    if historical_context:
        historical_section = f"""
## Historical Context
{historical_context}
"""

    prompt = f"""You are a senior geospatial economic analyst specializing in port and logistics activity assessment using satellite remote sensing data. You have 15 years of experience interpreting Sentinel-2 multispectral imagery for economic intelligence purposes.

## Task
Analyze the following satellite scene statistics for {site_config['name']} and produce a structured economic activity assessment. This data was captured on {acquisition_date} from a Sentinel-2 L2A scene (atmospherically corrected surface reflectance).

## Site Context
- **Location**: {site_config['name']}
- **Description**: {site_config['description']}
- **Bounding Box**: {site_config['bbox']} (WGS84: west, south, east, north)

## Scene Statistics
```json
{stats_json}
```
{historical_section}

## Spectral Index Reference Guide
Use this to interpret the statistics:

**NDVI (Normalized Difference Vegetation Index)**
- > 0.5: Dense vegetation (forests, parks)
- 0.2–0.5: Sparse/moderate vegetation
- 0.0–0.2: Bare soil, sparse vegetation
- < 0.0: Water, built surfaces, vessel hulls, wet areas

**NDWI (Normalized Difference Water Index)**
- > 0.3: Open water (clear confidence)
- 0.0–0.3: Turbid water, mixed water/land, wet surfaces
- < 0.0: Built environment, dry land

**MNDWI (Modified NDWI)**
- More accurate than NDWI for industrial/port water (removes built-up false positives)
- > 0.2: High confidence water
- Negative: Built surfaces, industrial areas

**Brightness (Visible bands average)**
- High brightness in port areas: container stacks, vessel superstructures, fresh concrete, active quays
- Low brightness: water absorbs light, vegetation is darker
- Top 5% bright pixels in port context often correspond to large vessels or dense container loading zones

**NDBI (Normalized Difference Built-up Index)**
- > 0.1: Strong built-up signal (warehouses, pavement, industrial facilities)
- Near 0: Mixed urban
- < 0: Vegetation or water

## Analysis Instructions
1. Interpret each spectral index in the context of this specific port/logistics site
2. Identify what the brightness distribution tells us about current vessel or container activity
3. Assess the land/water fractions for consistency with expected port operations
4. Estimate relative activity level compared to a "baseline" port scene
5. Flag any anomalies that might indicate unusual economic activity (e.g., unusually low brightness could indicate reduced vessel traffic; high NDWI variance could indicate unusual water presence)
6. Note confidence levels and limitations explicitly

## Required Output Format
Respond ONLY with a valid JSON object matching this exact schema:

```json
{{
  "site": "string - site name",
  "acquisition_date": "string - YYYY-MM-DD",
  "analysis_timestamp": "string - ISO datetime of this analysis",
  "economic_activity_summary": {{
    "overall_activity_level": "string - one of: HIGH / ABOVE_AVERAGE / AVERAGE / BELOW_AVERAGE / LOW",
    "confidence": "string - one of: HIGH / MEDIUM / LOW",
    "confidence_rationale": "string - why this confidence level",
    "primary_signals": ["array of strings - top 3-5 key observations driving the assessment"],
    "vessel_traffic_proxy": {{
      "assessment": "string - HIGH/MODERATE/LOW/INDETERMINATE",
      "evidence": "string - specific statistics supporting this"
    }},
    "infrastructure_utilization": {{
      "assessment": "string - HIGH/MODERATE/LOW/INDETERMINATE",
      "evidence": "string - specific statistics supporting this"
    }},
    "water_activity": {{
      "assessment": "string - description of water body conditions",
      "evidence": "string - NDWI/MNDWI statistics used"
    }}
  }},
  "quantitative_findings": {{
    "brightness_interpretation": "string - economic meaning of brightness statistics",
    "ndvi_interpretation": "string - what vegetation signal means here",
    "water_fraction_interpretation": "string - what water fraction tells us",
    "built_environment_signal": "string - NDBI interpretation"
  }},
  "anomalies": [
    {{
      "description": "string - what