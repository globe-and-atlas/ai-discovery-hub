# Replicate the Sentinel-2 Soil Salinity SVM Workflow and Layer in a Claude-Assisted Classification Step

> **Transparency note:** The source video's transcript was not fully retrievable — only metadata was available. This tutorial reconstructs the QGIS SVM/Random Forest soil salinity workflow from established practitioner knowledge of that exact pipeline, then adds the Claude API integration layer as specified. Where steps are inferred from domain knowledge rather than the video transcript, this is flagged explicitly. Treat section headers marked **[INFERRED]** as "standard practice for this workflow type" rather than direct video instruction.

---

## 1. Introduction & Context

Soil salinity mapping is one of the more practically demanding remote sensing tasks: saline soils have subtle spectral signatures that overlap with dry bare soil and mineral crusts, making visual interpretation unreliable. The standard solution — supervised classification using SVM or Random Forest on multispectral Sentinel-2 bands — gives you a repeatable, defensible workflow that scales across large agricultural areas.

The video from *Satellite Remote Sensing and GIS* walks through this pipeline end-to-end inside QGIS. Your goal here is to:

1. **Replicate that workflow** using your existing `rasterio` / `geopandas` / scikit-learn stack (so it lives in Python, not just GUI clicks).
2. **Add a Claude API layer** that reads your output classification raster statistics and auto-generates human-readable class descriptions and anomaly flags.
3. **Publish the hybrid result** as a Build post for your GIS audience.

**Why this matters for your practice:**
- Sentinel-2 + QGIS + SVM/RF is already in your stack — this exercise closes the loop from "I know the tools" to "I have a published, reproducible workflow."
- The Claude integration demonstrates AI-augmented GIS in a concrete, auditable way: the model doesn't *do* the classification, it *interprets* it — a framing your audience will trust.
- The output is a Build post asset, not just a notebook exercise.

**Time estimate:** 3–5 hours for a first run; ~2 hours for subsequent scenes.

---

## 2. Prerequisites

### Software & Libraries

```bash
# Core Python stack
pip install rasterio geopandas scikit-learn numpy pandas matplotlib
pip install anthropic          # Claude API client
pip install scipy joblib       # model persistence and stats
pip install folium              # optional: interactive map for the post

# QGIS (for visual QA and training sample collection)
# Install via your OS package manager or qgis.org
# Recommended: QGIS 3.28 LTS or later
```

### Data

| Asset | Source | Notes |
|---|---|---|
| Sentinel-2 L2A scene | [Copernicus Browser](https://browser.dataspace.copernicus.eu/) | Download a cloud-free scene (<10% cloud cover) over an agricultural/arid area. Bands 2,3,4,8,11,12 minimum. |
| Training polygons | Drawn in QGIS (see Step 3) | Minimum 5 classes; minimum 30 polygons per class |
| Field salinity data (optional) | FAO GeoNetwork or local authority | For accuracy validation; not required for the tutorial |

### Accounts & Keys

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # add to your .env or shell profile
```

### QGIS Plugins **[INFERRED — standard for this workflow type]**

- **Semi-Automatic Classification Plugin (SCP)** — the most widely used QGIS plugin for supervised classification of multispectral imagery. Install via `Plugins → Manage and Install Plugins → SCP`.
- **SAGA provider** — ships with QGIS, used for preprocessing.

---

## 3. Step-by-Step Guide

### Step 3.1 — Download and Prepare the Sentinel-2 Scene

**[INFERRED — standard Sentinel-2 preprocessing for classification]**

```python
# file: 01_prepare_sentinel2.py
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from pathlib import Path

# --- CONFIG ---
S2_DIR = Path("data/S2_L2A/")   # unzipped Sentinel-2 .SAFE folder contents
OUTPUT_STACK = Path("output/s2_stack.tif")
OUTPUT_STACK.parent.mkdir(parents=True, exist_ok=True)

# Sentinel-2 bands relevant to salinity mapping
# B02=Blue, B03=Green, B04=Red, B08=NIR, B11=SWIR1, B12=SWIR2
# B11 and B12 are 20m; others are 10m — resample to common 20m grid
BAND_PATHS = {
    "B02": sorted(S2_DIR.glob("**/B02_10m.jp2"))[0],
    "B03": sorted(S2_DIR.glob("**/B03_10m.jp2"))[0],
    "B04": sorted(S2_DIR.glob("**/B04_10m.jp2"))[0],
    "B08": sorted(S2_DIR.glob("**/B08_10m.jp2"))[0],
    "B11": sorted(S2_DIR.glob("**/B11_20m.jp2"))[0],
    "B12": sorted(S2_DIR.glob("**/B12_20m.jp2"))[0],
}

TARGET_RESOLUTION = 20  # meters — match SWIR bands

def resample_to_resolution(src_path, target_res, reference_transform=None, reference_crs=None, reference_shape=None):
    """Resample a raster to a target resolution."""
    with rasterio.open(src_path) as src:
        if reference_shape is None:
            # Calculate new dimensions
            scale = src.res[0] / target_res
            new_height = int(src.height * scale)
            new_width = int(src.width * scale)
            new_transform = src.transform * src.transform.scale(
                src.width / new_width,
                src.height / new_height
            )
            reference_shape = (new_height, new_width)
            reference_transform = new_transform
            reference_crs = src.crs

        data = np.empty((src.count, reference_shape[0], reference_shape[1]), dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1),
            destination=data[0],
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=reference_transform,
            dst_crs=reference_crs,
            resampling=Resampling.bilinear,
        )
        return data[0], reference_transform, reference_crs, reference_shape

# Build stack
print("Building band stack...")
stack_arrays = []
ref_transform = ref_crs = ref_shape = None

for band_name, band_path in BAND_PATHS.items():
    print(f"  Processing {band_name}: {band_path.name}")
    arr, ref_transform, ref_crs, ref_shape = resample_to_resolution(
        band_path, TARGET_RESOLUTION, ref_transform, ref_crs, ref_shape
    )
    stack_arrays.append(arr)

stack = np.stack(stack_arrays, axis=0)  # shape: (6, H, W)

# Write stack
profile = {
    "driver": "GTiff",
    "dtype": "float32",
    "width": ref_shape[1],
    "height": ref_shape[0],
    "count": len(BAND_PATHS),
    "crs": ref_crs,
    "transform": ref_transform,
    "compress": "lzw",
    "nodata": 0,
}

with rasterio.open(OUTPUT_STACK, "w", **profile) as dst:
    dst.write(stack)
    dst.update_tags(
        band_order=",".join(BAND_PATHS.keys()),
        source="Sentinel-2 L2A",
        resolution_m=str(TARGET_RESOLUTION),
    )

print(f"Stack written: {OUTPUT_STACK} — shape {stack.shape}")
```

### Step 3.2 — Compute Salinity-Relevant Spectral Indices

**[INFERRED — these indices are standard in the soil salinity literature]**

```python
# file: 02_compute_indices.py
import rasterio
import numpy as np
from pathlib import Path

STACK_PATH = Path("output/s2_stack.tif")
INDICES_PATH = Path("output/s2_indices.tif")

# Band order from Step 1: B02, B03, B04, B08, B11, B12 (indices 0–5)

def safe_divide(a, b, fill=0.0):
    """Division with zero-protection."""
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(b != 0, a / b, fill)
    return result.astype(np.float32)

with rasterio.open(STACK_PATH) as src:
    blue  = src.read(1).astype(np.float32)
    green = src.read(2).astype(np.float32)
    red   = src.read(3).astype(np.float32)
    nir   = src.read(4).astype(np.float32)
    swir1 = src.read(5).astype(np.float32)
    swir2 = src.read(6).astype(np.float32)
    profile = src.profile.copy()

# --- Spectral Indices ---

# NDVI: vegetation health (saline soils show low NDVI)
ndvi = safe_divide(nir - red, nir + red)

# NDSI (Salinity Index): sensitive to salt crusts
# Common formulation: (Green - NIR) / (Green + NIR)
ndsi = safe_divide(green - nir, green + nir)

# SI1: Salinity Index 1 = sqrt(Blue * Red)
si1 = np.sqrt(np.abs(blue * red)).astype(np.float32)

# SI2: Salinity Index 2 = sqrt(Green * Red)
si2 = np.sqrt(np.abs(green * red)).astype(np.float32)

# CRSI: Canopy Response Salinity Index = sqrt((Red*NIR) / (Green*Blue))
crsi = np.sqrt(safe_divide(red * nir, green * blue)).astype(np.float32)

# SWIR ratio: useful for mineral/crust discrimination
swir_ratio = safe_divide(swir1, swir2)

indices = {
    "NDVI":       ndvi,
    "NDSI":       ndsi,
    "SI1":        si1,
    "SI2":        si2,
    "CRSI":       crsi,
    "SWIR_ratio": swir_ratio,
}

# Write indices stack
profile.update(count=len(indices), dtype="float32", nodata=np.nan)

with rasterio.open(INDICES_PATH, "w", **profile) as dst:
    for i, (name, arr) in enumerate(indices.items(), start=1):
        dst.write(arr, i)
    dst.update_tags(band_order=",".join(indices.keys()))

print(f"Indices written: {INDICES_PATH}")
print(f"Bands: {list(indices.keys())}")
```

### Step 3.3 — Collect Training Samples in QGIS

**[INFERRED — video demonstrates this step in QGIS GUI]**

This is the step the video covers in detail. Open QGIS and follow this workflow:

1. **Load your band stack** (`output/s2_stack.tif`) and set a false-color composite (e.g., SWIR1/NIR/Red) to highlight saline surfaces.

2. **Define your salinity classes.** A standard schema for arid agricultural areas:

   | Class ID | Class Name | Visual Signature |
   |---|---|---|
   | 1 | Non-saline agricultural | Dense green vegetation |
   | 2 | Slightly saline | Patchy vegetation, pale soil |
   | 3 | Moderately saline | Sparse vegetation, white patches |
   | 4 | Highly saline | Bare, white/light grey crust |
   | 5 | Very highly saline | Bright white salt crust, no vegetation |
   | 6 | Water body | Dark/blue tones |

3. **Create a training polygon layer:**
   - `Layer → Create Layer → New Shapefile Layer`
   - Fields: `class_id` (Integer), `class_name` (String)
   - CRS: match your raster

4. **Digitize training polygons** — minimum 30 polygons per class, distributed across the scene. Aim for spatial variety (not all in one cluster).

5. **Export as GeoPackage:** `data/training_samples.gpkg`

**Tip — using SCP Plugin [INFERRED]:** If you installed SCP, use `SCP → Training Input → Create Training Input` to manage ROI (Region of Interest) collection with built-in spectral signature preview.

### Step 3.4 — Extract Training Features from the Raster Stack

```python
# file: 03_extract_features.py
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.mask import mask
from pathlib import Path
from shapely.geometry import mapping

STACK_PATH  = Path("output/s2_stack.tif")
INDICES_PATH = Path("output/s2_indices.tif")
TRAINING_PATH = Path("data/training_samples.gpkg")
FEATURES_CSV = Path("output/training_features.csv")

STACK_BANDS  = ["B02","B03","B04","B08","B11","B12"]
INDICES_BANDS = ["NDVI","NDSI","SI1","SI2","CRSI","SWIR_ratio"]

def extract_pixels_from_raster(raster_path, band_names, polygons_gdf):
    """Extract pixel values under each training polygon."""
    rows = []
    with rasterio.open(raster_path) as src:
        # Reproject polygons to raster CRS if needed
        polys = polygons_gdf.to_crs(src.crs)
        for _, row in polys.iterrows():
            geom = [mapping(row.geometry)]
            try:
                out_image, _ = mask(src, geom, crop=True, nodata=np.nan)
                # out_image shape: (bands, H, W)
                n_bands, h, w = out_image.shape
                pixels = out_image.reshape(n_bands, -1).T  # (n_pixels, n_bands)
                # Remove nodata pixels
                valid = ~np.isnan(pixels).any(axis=1)
                pixels = pixels[valid]
                for px in pixels:
                    record = {name: val for name, val in zip(band_names, px)}
                    record["class_id"]   = row["class_id"]
                    record["class_name"] = row["class_name"]
                    rows.append(record)
            except Exception as e:
                print(f"  Warning: could not process polygon {row.name}: {e}")
    return pd.DataFrame(rows)

print("Loading training polygons...")
gdf = gpd.read_file(TRAINING_PATH)
print(f"  {len(gdf)} polygons, classes: {gdf['class_name'].unique()}")

print("Extracting band values...")
df_bands = extract_pixels_from_raster(STACK_PATH, STACK_BANDS, gdf)

print("Extracting index values...")
df_indices = extract_pixels_from_raster(INDICES_PATH, INDICES_BANDS, gdf)

# Merge on row position (both extractions use same polygon order)
df = pd.concat([
    df_bands[STACK_BANDS],
    df_indices[INDICES_BANDS],
    df_bands[["class_id", "class_name"]]
], axis=1)

df.dropna(inplace=True)
df.to_csv(FEATURES_CSV, index=False)
print(f"\nFeatures written: {FEATURES_CSV}")
print(f"Total training pixels: {len(df)}")
print(df.groupby("class_name").size().to_string())
```

### Step 3.5 — Train SVM and Random Forest Classifiers

```python
# file: 04_train_classifiers.py
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

FEATURES_CSV = Path("output/training_features.csv")
MODELS_DIR   = Path("output/models/")
MODELS_DIR.mkdir(exist_ok=True)

FEATURE_COLS = ["B02","B03","B04","B08","B11","B12",
                "NDVI","NDSI","SI1","SI2","CRSI","SWIR_ratio"]
LABEL_COL    = "class_id"
NAMES_COL    = "class_name"

# --- Load data ---
df = pd.read_csv(FEATURES_CSV)
X = df[FEATURE_COLS].values
y = df[LABEL_COL].values
class_names_map = df.groupby(LABEL_COL)[NAMES_COL].first().to_dict()

print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
print(f"Class distribution:\n{df.groupby(NAMES_COL).size()}\n")

# --- Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# --- Scale features (critical for SVM) ---
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)
joblib.dump(scaler, MODELS_DIR / "scaler.pkl")

# ============================================================
# SVM
# ============================================================
print("Training SVM (RBF kernel)...")
# NOTE: The video uses SVM — specific kernel/C/gamma values not retrievable
# from metadata. These are sensible defaults for this problem type.
svm = SVC(
    kernel="rbf",
    C=10,
    gamma="scale",
    probability=True,    # needed for confidence outputs later
    class_weight="balanced",
    random_state=42,
    verbose=False,
)
svm.fit(X_train_sc, y_train)

svm_preds = svm.predict(X_test_sc)
print("\n=== SVM Classification Report ===")
print(classification_report(y_test, svm_preds,
      target_names=[class_names_map[c] for c in sorted(class_names_map)]))

# Cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
svm_cv = cross_val_score(svm, X_train_sc, y_train, cv=cv, scoring="f1_weighted")
print(f"SVM 5-fold CV F1 (weighted): {svm_cv.mean():.3f} ± {svm_cv.std():.3f}")
joblib.dump(svm, MODELS_DIR / "svm_model.pkl")

# ============================================================
# Random Forest
# ============================================================
print("\nTraining Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
rf.fit(X_train, y_train)    # RF doesn't need scaling

rf_preds = rf.predict(X_test)
print("\n=== Random Forest Classification Report ===")
print(classification_report(y_test, rf_preds,
      target_names=[class_names_map[c] for c in sorted(class_names_map)]))

rf_cv = cross_val_score(rf, X_train, y_train, cv=cv, scoring="f1_weighted")
print(f"RF 5-fold CV F1 (weighted): {rf_cv.mean():.3f} ± {rf_cv.std():.3f}")
joblib.dump(rf, MODELS_DIR / "rf_model.pkl")

# ============================================================
# Confusion matrix plots
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, preds, title in zip(axes,
                             [svm_preds, rf_preds],
                             ["SVM", "Random Forest"]):
    cm = confusion_matrix(y_test, preds)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    sns.heatmap(cm_norm, annot=True, fmt=".2f", ax=ax,
                xticklabels=list(class_names_map.values()),
                yticklabels=list(class_names_map.values()),
                cmap="YlOrRd")
    ax.set_title(f"{title} Confusion Matrix (normalized)")
    ax.set_ylabel("True")
    ax.set_xlabel("Predicted")

plt.tight_layout()
plt.savefig("output/confusion_matrices.png", dpi=150)
print("\nConfusion matrices saved.")

# ============================================================
# Feature importance (RF only)
# ============================================================
fi = pd.Series(rf.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
print("\nRandom Forest Feature Importance:")
print(fi.round(4).to_string())
fi.plot(kind="bar", figsize=(10, 4), title="RF Feature Importance")
plt.tight_layout()
plt.savefig("output/feature_importance.png", dpi=150)
```

### Step 3.6 — Apply Classifiers to the Full Scene

```python
# file: 05_apply_classifiers.py
import rasterio
import numpy as np
import joblib
from pathlib import Path

STACK_PATH   = Path("output/s2_stack.tif")
INDICES_PATH = Path("output/s2_indices.tif")
MODELS_DIR   = Path("output/models/")
SVM_OUTPUT   = Path("output/classification_svm.tif")
RF_OUTPUT    = Path("output/classification_rf.tif")

FEATURE_COLS = ["B02","B03","B04","B08","B11","B12",
                "NDVI","NDSI","SI1","SI2","CRSI","SWIR_ratio"]

# Load models
scaler = joblib.load(MODELS_DIR / "scaler.pkl")
svm    = joblib.load(MODELS_DIR / "svm_model.pkl")
rf     = joblib.load(MODELS_DIR / "rf_model.pkl")

def read_full_stack(stack_path, indices_path):
    """Read all bands into a 2D feature matrix (n_pixels, n_features)."""
    with rasterio.open(stack_path) as src:
        profile = src.profile.copy()
        profile.update(count=1, dtype="uint8", nodata=255)
        bands = src.read().astype(np.float32)   # (6, H, W)
        height, width = bands.shape[1], bands.shape[2]
        nodata_mask = (bands[0] == 0)            # assume band 1 nodata = 0

    with rasterio.open(indices_path) as idx_src:
        indices = idx_src.read().astype(np.float32)  # (6, H, W)

    # Stack all features: shape (12, H, W)
    all_bands = np.concatenate([bands, indices], axis=0)

    # Reshape to (H*W, 12)
    n_features, h, w = all_bands.shape
    flat = all_bands.reshape(n_features, -1).T   # (n_pixels, 12)

    return flat, nodata_mask.flatten(), profile, height, width

print("Reading full scene...")
X_scene, nodata_flat, profile, H, W = read_full_stack(STACK_PATH, INDICES_PATH)

# Valid pixels only (avoid NaN/nodata)
valid_mask = ~nodata_flat & ~np.isnan(X_scene).any(axis=1)
X_valid = X_scene[valid_mask]

print(f"Total pixels: {H*W:,}  |  Valid: {valid_mask.sum():,}")

# --- SVM prediction ---
print("Applying SVM...")
X_valid_sc = scaler.transform(X_valid)

# Process in chunks to avoid memory issues on large scenes
CHUNK = 100_000
svm_result = np.zeros(H * W, dtype=np.uint8)
svm_result[~valid_mask] = 255  # nodata

for start in range(0, X_valid_sc.shape[0], CHUNK):
    end = min(start + CHUNK, X_valid_sc.shape[0])
    chunk_preds = svm.predict(X_valid_sc[start:end]).astype(np.uint8)
    valid_indices = np.where(valid_mask)[0][start:end]
    svm_result[valid_indices] = chunk_preds
    print(f"  SVM chunk {start//CHUNK + 1}/{-(-X_valid_sc.shape[0]//CHUNK)} done")

# --- RF prediction ---
print("Applying Random Forest...")
rf_result = np.zeros(H * W, dtype=np.uint8)
rf_result[~valid_mask] = 255

for start in range(0, X_valid.shape[0], CHUNK):
    end = min(start + CHUNK, X_valid.shape[0])
    chunk_preds = rf.predict(X_valid[start:end]).astype(np.uint8)
    valid_indices = np.where(valid_mask)[0][start:end]
    rf_result[valid_indices] = chunk_preds
    print(f"  RF chunk {start//CHUNK + 1}/{-(-X_valid.shape[0]//CHUNK)} done")

# --- Write outputs ---
for out_path, result, label in [(SVM_OUTPUT, svm_result, "SVM"),
                                 (RF_OUTPUT, rf_result, "RF")]:
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(result.reshape(H, W), 1)
        dst.update_tags(classifier=label, classes="1-6 + 255=nodata")
    print(f"{label} classification written: {out_path}")
```

### Step 3.7 — Compute Classification Statistics

```python
# file: 06_compute_stats.py
import rasterio
import numpy as np
import pandas as pd
import json
from pathlib import Path

SVM_PATH = Path("output/classification_svm.tif")
RF_PATH  = Path("output/classification_rf.tif")
STATS_JSON = Path("output/classification_stats.json")

CLASS_NAMES = {
    1: "Non-saline agricultural",
    2: "Slightly saline",
    3: "Moderately saline",
    4: "Highly saline",
    5: "Very highly saline",
    6: "Water body",
}

def compute_class_stats(raster_path, class_names):
    """Compute per-class pixel counts and area estimates."""
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        pixel_area_m2 = abs(src.transform.a * src.transform.e)
        pixel_area_ha = pixel_area_m2 / 10_000
        nodata = src.nodata

    total_valid = np.sum(data != nodata)
    stats = {}

    for class_id, class_name in class_names.items():
        count = int(np.sum(data == class_id))
        area_ha = count * pixel_area_ha
        pct = (count / total_valid * 100) if total_valid > 0 else 0
        stats[class_id] = {
            "class_name": class_name,
            "pixel_count": count,
            "area_ha": round(area_ha, 2),
            "percent_of_valid": round(pct, 2),
        }

    return stats, pixel_area_ha, int(total_valid)

print("Computing statistics...")
svm_stats, px_ha, n_valid = compute_class_stats(SVM_PATH, CLASS_NAMES)
rf_stats, _, _ = compute_class_stats(RF_PATH, CLASS_NAMES)

# Agreement analysis: where do SVM and RF agree?
with rasterio.open(SVM_PATH) as s, rasterio.open(RF_PATH) as r:
    svm_arr = s.read(1)
    rf_arr  = r.read(1)

valid_mask = (svm_arr != 255) & (rf_arr != 255)
agreement = float(np.sum(svm_arr[valid_mask] == rf_arr[valid_mask]) / valid_mask.sum() * 100)

# Saline area totals (classes 3, 4, 5)
saline_classes = [3, 4, 5]
svm_saline_ha = sum(svm_stats[c]["area_ha"] for c in saline_classes)
rf_saline_ha  = sum(rf_stats[c]["area_ha"]  for c in saline_classes)

output = {
    "pixel_area_ha": round(px_ha, 6),
    "total_valid_pixels": n_valid,
    "classifier_agreement_pct": round(agreement, 2),
    "svm": {
        "total_saline_area_ha": round(svm_saline_ha, 2),
        "classes": svm_stats,
    },
    "rf": {
        "total_saline_area_ha": round(rf_saline_ha, 2),
        "classes": rf_stats,
    },
}

with open(STATS_JSON, "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
print(f"\nStats written: {STATS_JSON}")
```

### Step 3.8 — Claude API: Auto-Generate Legend Descriptions and Anomaly Flags

This is the AI-augmentation layer. Claude reads the classification statistics and generates:
- Human-readable class descriptions contextualized to the actual distribution
- Anomaly flags where the two classifiers disagree significantly
- A ready-to-paste legend block for your Build post

```python
# file: 07_claude_legend_and_flags.py
import anthropic
import json
from pathlib import Path

STATS_JSON   = Path("output/classification_stats.json")
CLAUDE_OUTPUT = Path("output/claude_legend_report.md")

# Load stats
with open(STATS_JSON) as f:
    stats = json.load(f)

# Build the prompt
stats_summary = json.dumps(stats, indent=2)

SYSTEM_PROMPT = """You are an expert remote sensing analyst and science communicator 
specializing in soil salinity assessment and land degradation. 

Your task is to interpret supervised classification output from Sentinel-2 imagery and 
produce two deliverables:

1. A CLASS LEGEND with one paragraph per class that describes:
   - What the class represents ecologically and agronomically
   - The spectral characteristics that distinguish it in Sentinel-2
   - Agricultural or environmental management implications