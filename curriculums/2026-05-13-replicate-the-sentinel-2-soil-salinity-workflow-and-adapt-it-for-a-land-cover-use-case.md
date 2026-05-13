# Replicate the Sentinel-2 Soil Salinity Workflow & Adapt It for Land Cover Classification

## A Hands-On Curriculum for SVM and Random Forest Classification in QGIS

---

## 1. Introduction & Context

### What Is This?

This curriculum walks you through replicating a supervised machine learning classification workflow on Sentinel-2 satellite imagery inside QGIS — first following the soil salinity mapping approach from the source tutorial, then **adapting it for a land cover classification use case** relevant to your editorial work on Globe & Atlas.

You will train two classifiers — **Support Vector Machine (SVM)** and **Random Forest (RF)** — compare their accuracy, and produce a publishable "The Build" post draft documenting the workflow.

### Why Is This Worth Learning?

- **Sentinel-2** is the backbone of many environmental monitoring workflows. Its 13 multispectral bands (10m–60m resolution, freely available) make it uniquely suited to land cover, agriculture, and environmental change mapping.
- **Supervised classification** is the bridge between raw satellite pixels and meaningful geographic labels — a core skill for any remote sensing practitioner.
- **SVM and Random Forest** are the two workhorses of remote sensing classification. Understanding how they differ in practice (not just theory) makes you a sharper analyst and a more credible writer.
- **The editorial angle**: Land cover change stories — deforestation, urban sprawl, wetland loss — are perennial Globe & Atlas subjects. Being able to produce your own classified maps gives you original data for every story.

### What You'll Produce

1. A classified Sentinel-2 land cover raster for a chosen area of interest (AOI)
2. Accuracy assessment metrics (confusion matrix, overall accuracy, Kappa coefficient) for both SVM and RF
3. A draft "The Build" post documenting the workflow end-to-end

---

## 2. Prerequisites

### Software

| Requirement | Version | Notes |
|---|---|---|
| QGIS | 3.28 LTS or later | Download from [qgis.org](https://qgis.org) |
| QGIS Plugin: Orfeo Toolbox (OTB) | Latest | Provides SVM and RF classifiers |
| QGIS Plugin: Semi-Automatic Classification Plugin (SCP) | 8.x | Training sample collection and accuracy assessment |
| Python | 3.9+ | For Sentinel Hub API calls |
| sentinelhub Python library | Latest | `pip install sentinelhub` |

### Accounts & API Access

- **Sentinel Hub account** with an active OAuth client (Client ID + Client Secret)
- Alternatively: **Copernicus Browser** account for manual downloads (free)

### Knowledge

- Basic QGIS navigation (add layers, zoom, pan, identify features)
- Basic understanding of raster data and coordinate reference systems (CRS)
- Familiarity with Python at a beginner level (for the API download step)
- You have watched (or will watch alongside this curriculum) the source tutorial: [YouTube — Supervised Classification for Soil Salinity in QGIS](https://www.youtube.com/watch?v=6CuqNYTFIpI)

### Recommended Background Reading

- [Sentinel-2 User Guide (ESA)](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [SCP Documentation](https://fromgistors.blogspot.com/p/semi-automatic-classification-plugin.html)

---

## 3. Step-by-Step Guide

This guide is organized into **six phases**:

```
Phase 1 → Choose Your AOI & Land Cover Use Case
Phase 2 → Download Sentinel-2 Imagery via Sentinel Hub API
Phase 3 → Prepare the Image in QGIS
Phase 4 → Collect Training Samples
Phase 5 → Run SVM and Random Forest Classification
Phase 6 → Accuracy Assessment & Comparison
```

---

### Phase 1: Choose Your AOI & Land Cover Use Case

#### 1.1 Select a Globe & Atlas-Relevant Land Cover Theme

Choose **one** of the following use cases (or define your own):

| Use Case | Suggested AOI | Key Classes |
|---|---|---|
| Deforestation monitoring | Amazon basin, Borneo | Forest, Cleared land, Regrowth, Water, Urban |
| Urban expansion | Nairobi, Dhaka, Phoenix | Urban/Built-up, Bare soil, Vegetation, Water |
| Wetland loss | Mesopotamian marshes, Florida Everglades | Open water, Marsh/wetland, Cropland, Dry land |
| Agricultural mapping | Nile Delta, Punjab, Iowa | Irrigated crops, Rain-fed crops, Fallow, Desert, Water |
| Coastal land cover | Mekong Delta, Bangladesh coast | Mangrove, Rice paddy, Water, Urban, Bare sand |

> **Recommendation for a first run**: Urban expansion around a fast-growing city. Urban/non-urban class boundaries are visually clear, making training sample collection straightforward.

#### 1.2 Define Your AOI Bounding Box

Write down your bounding box in WGS84 decimal degrees:

```
AOI_BBOX = {
    "west":  <min_longitude>,
    "south": <min_latitude>,
    "east":  <max_longitude>,
    "north": <max_latitude>
}
```

**Example (Nairobi, Kenya):**
```
AOI_BBOX = {
    "west":  36.65,
    "south": -1.45,
    "east":  37.10,
    "north": -1.10
}
```

> **Size guidance**: Keep your AOI under ~50×50 km for your first run. Larger areas slow classification significantly and complicate training sample collection.

#### 1.3 Choose a Target Date Range

Pick a **dry season** window for your AOI to minimize cloud cover. Aim for scenes with <10% cloud coverage.

```
DATE_FROM = "2023-11-01"
DATE_TO   = "2024-01-31"
```

---

### Phase 2: Download Sentinel-2 Imagery via Sentinel Hub API

#### 2.1 Install and Configure the sentinelhub Library

```bash
pip install sentinelhub
```

Configure your credentials (run once):

```bash
sentinelhub.config --instance_id YOUR_INSTANCE_ID \
                   --sh_client_id YOUR_CLIENT_ID \
                   --sh_client_secret YOUR_CLIENT_SECRET
```

Or configure in Python:

```python
from sentinelhub import SHConfig

config = SHConfig()
config.sh_client_id     = "YOUR_CLIENT_ID"
config.sh_client_secret = "YOUR_CLIENT_SECRET"
config.save()
```

#### 2.2 Download a Sentinel-2 L2A Multiband Image

The following script downloads a cloud-free Sentinel-2 Level-2A composite as a GeoTIFF with all bands needed for land cover classification.

```python
# sentinel2_download.py
# Downloads Sentinel-2 L2A bands for land cover classification

from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    bbox_to_dimensions,
)
import numpy as np
import os

# ── Configuration ────────────────────────────────────────────────────────────
config = SHConfig()

AOI_BBOX = BBox(
    bbox=[36.65, -1.45, 37.10, -1.10],  # west, south, east, north
    crs=CRS.WGS84
)

DATE_FROM = "2023-11-01"
DATE_TO   = "2024-01-31"
RESOLUTION = 10  # metres per pixel (use 20 for faster processing)
OUTPUT_DIR = "./sentinel2_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Evalscript: return key bands for land cover ───────────────────────────────
# Bands: B02(Blue), B03(Green), B04(Red), B08(NIR),
#        B11(SWIR1), B12(SWIR2), B05(RedEdge1), B06(RedEdge2)
# Returned as Float32 surface reflectance (÷10000 to get 0–1 range)

EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["B02","B03","B04","B05","B06","B08","B11","B12"],
            units: "REFLECTANCE"
        }],
        output: {
            bands: 8,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(sample) {
    return [
        sample.B02,
        sample.B03,
        sample.B04,
        sample.B05,
        sample.B06,
        sample.B08,
        sample.B11,
        sample.B12
    ];
}
"""

# ── Build request ─────────────────────────────────────────────────────────────
size = bbox_to_dimensions(AOI_BBOX, resolution=RESOLUTION)
print(f"Image dimensions: {size[0]} x {size[1]} pixels")

request = SentinelHubRequest(
    evalscript=EVALSCRIPT,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=(DATE_FROM, DATE_TO),
            mosaicking_order="leastCC",   # least cloud cover first
        )
    ],
    responses=[
        SentinelHubRequest.output_response("default", MimeType.TIFF)
    ],
    bbox=AOI_BBOX,
    size=size,
    config=config,
    data_folder=OUTPUT_DIR,
)

# ── Download ──────────────────────────────────────────────────────────────────
print("Requesting image from Sentinel Hub...")
data = request.get_data(save_data=True)
print(f"Download complete. Files saved to: {OUTPUT_DIR}")
print(f"Array shape: {data[0].shape}")  # Expected: (rows, cols, 8)
```

Run the script:

```bash
python sentinel2_download.py
```

> **Output**: A GeoTIFF file in `./sentinel2_data/` with 8 bands. Note the exact filename — you'll need it in Phase 3.

#### 2.3 Alternative: Manual Download via Copernicus Browser

If you prefer a manual approach:

1. Go to [browser.dataspace.copernicus.eu](https://browser.dataspace.copernicus.eu)
2. Search for your AOI using the search box
3. Set date range and cloud cover filter (<10%)
4. Select **Sentinel-2 L2A** product
5. Download the full product (`.SAFE` folder)
6. Use QGIS → Raster → Miscellaneous → **Merge** to stack required bands into a single GeoTIFF

---

### Phase 3: Prepare the Image in QGIS

#### 3.1 Install Required QGIS Plugins

Open QGIS → **Plugins** → **Manage and Install Plugins**

Search for and install:
- `Semi-Automatic Classification Plugin` (SCP) — version 8.x
- `Orfeo Toolbox` (OTB) — if not bundled with your QGIS installation

> **OTB on Windows/Mac**: Download the standalone OTB package from [orfeotoolbox.org](https://www.orfeo-toolbox.org) and configure the path in QGIS → Settings → Options → Processing → OTB.

#### 3.2 Load Your Sentinel-2 Image

1. In QGIS, go to **Layer** → **Add Layer** → **Add Raster Layer**
2. Navigate to your downloaded GeoTIFF and click **Open**
3. The image will appear as a single layer with 8 bands

#### 3.3 Create a False Color Composite for Visual Interpretation

For land cover interpretation, a **NIR-Red-Green** composite (bands 6-3-2 in our stack) is ideal:

1. Right-click the layer → **Properties** → **Symbology**
2. Set **Render type**: Multiband color
3. Assign:
   - **Red band**: Band 6 (B08 — NIR)
   - **Green band**: Band 3 (B04 — Red)
   - **Blue band**: Band 2 (B03 — Green)
4. Click **Apply** → **OK**

> **Visual interpretation guide**:
> - Bright red/magenta → Dense vegetation
> - Dark blue/black → Water bodies
> - Pale pink/white → Urban/built-up or bare soil
> - Brown/tan → Sparse vegetation or cropland

#### 3.4 Check and Set the CRS

1. Right-click the layer → **Properties** → **Information**
2. Verify the CRS (should be a UTM zone matching your AOI, e.g., EPSG:32637 for Kenya)
3. If CRS is missing or incorrect: Right-click → **Set CRS** → search for the appropriate UTM zone
4. Set the project CRS to match: **Project** → **Properties** → **CRS**

#### 3.5 Calculate Spectral Indices (Optional but Recommended)

Adding spectral indices as extra bands improves classification accuracy. Calculate these using **Raster** → **Raster Calculator**:

**NDVI** (Normalized Difference Vegetation Index):
```
( "sentinel2@6" - "sentinel2@3" ) / ( "sentinel2@6" + "sentinel2@3" )
```
> Band 6 = NIR (B08), Band 3 = Red (B04)

**NDWI** (Normalized Difference Water Index):
```
( "sentinel2@2" - "sentinel2@6" ) / ( "sentinel2@2" + "sentinel2@6" )
```
> Band 2 = Green (B03), Band 6 = NIR (B08)

**NDBI** (Normalized Difference Built-up Index):
```
( "sentinel2@7" - "sentinel2@6" ) / ( "sentinel2@7" + "sentinel2@6" )
```
> Band 7 = SWIR1 (B11), Band 6 = NIR (B08)

Save each index as a separate GeoTIFF.

**Stack all bands + indices into one image** using SCP:

1. Open **SCP** panel → **Band set** tab
2. Click **+** to add a new band set
3. Add: your 8-band GeoTIFF + NDVI + NDWI + NDBI rasters
4. Click **Create virtual band set** → Save as `sentinel2_stack.vrt`

---

### Phase 4: Collect Training Samples

This is the most important — and most time-consuming — phase. Training sample quality determines classifier accuracy more than any algorithm choice.

#### 4.1 Define Your Land Cover Classes

Create a class scheme appropriate for your chosen use case. Example for **Urban Expansion**:

| Class ID | Class Name | Color Code | Min. Samples |
|---|---|---|---|
| 1 | Urban / Built-up | `#E74C3C` (Red) | 200 pixels |
| 2 | Dense Vegetation | `#27AE60` (Green) | 200 pixels |
| 3 | Sparse Vegetation / Cropland | `#F39C12` (Yellow) | 200 pixels |
| 4 | Water | `#2980B9` (Blue) | 100 pixels |
| 5 | Bare Soil / Bare Rock | `#BDC3C7` (Grey) | 150 pixels |

> **Rule of thumb**: Aim for at least 10× more training samples than input bands. With 11 bands (8 + 3 indices), aim for ≥110 pixels per class, preferably 200+.

#### 4.2 Set Up Training Sample Collection in SCP

1. Open **SCP** → **Training input** tab
2. Click the folder icon → Create a new training file: `land_cover_training.scp`
3. In the **Macroclasses** section, add each class from your table above
4. Assign Class ID, name, and color for each

#### 4.3 Collect Training Samples (Digitizing)

For each land cover class:

1. In SCP toolbar, click **Activate ROI creation** (pencil icon)
2. Select the target class from the dropdown
3. Click on the map to create a **Region of Interest (ROI)** — a small polygon over a clearly identifiable area
4. Review the spectral signature plot in SCP → **Spectral signature** tab to confirm the sample is spectrally consistent
5. Click **Save ROI** to add it to the training set
6. Repeat across the entire AOI, sampling different geographic sub-regions

> **Quality tips**:
> - Sample from across the full AOI, not just one corner
> - Avoid class boundaries (mixed pixels)
> - For urban: sample different building types (rooftops, roads, parking lots) separately within the urban class
> - Use **Google Satellite** as a reference: Add XYZ tile layer in QGIS with URL: `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`

#### 4.4 Verify Training Sample Separability

In SCP → **Spectral signature** tab:

1. Select all classes
2. Click **Calculate spectral distances**
3. Review the **Jeffries-Matusita Distance** table
4. Classes with distance **< 1.5** are poorly separated — re-collect samples for those classes

```
✅ JM distance > 1.9 = Excellent separability
⚠️  JM distance 1.5–1.9 = Acceptable
❌ JM distance < 1.5 = Poor — resample these classes
```

---

### Phase 5: Run SVM and Random Forest Classification

#### 5.1 Split Training Data into Train/Test Sets

Before classifying, reserve 30% of your samples for accuracy assessment:

In SCP → **Training input** → **Export** → Export the `.scp` file as a CSV

Then in Python:

```python
# split_training.py
# Splits SCP training CSV into 70% train / 30% test

import pandas as pd
from sklearn.model_selection import train_test_split

# Load exported training data (adjust column names to match SCP export)
df = pd.read_csv("land_cover_training_export.csv")

train_df, test_df = train_test_split(
    df,
    test_size=0.30,
    stratify=df["class_id"],   # ensure all classes represented in both splits
    random_state=42
)

train_df.to_csv("training_70pct.csv", index=False)
test_df.to_csv("testing_30pct.csv",  index=False)

print(f"Training samples: {len(train_df)}")
print(f"Testing samples:  {len(test_df)}")
print("\nClass distribution in training set:")
print(train_df["class_id"].value_counts().sort_index())
```

> **In QGIS SCP alternative**: You can manage this split entirely within SCP by using the "K-fold cross-validation" option in the classification settings.

#### 5.2 Run Random Forest Classification (via SCP)

1. Open **SCP** → **Classification** tab
2. Under **Input**, select your `sentinel2_stack.vrt` as the input image
3. Under **Training input**, confirm `land_cover_training.scp` is loaded
4. Set **Algorithm**: `Random Forest`
5. Set parameters:
   - **Number of trees**: `100`
   - **Max depth**: `0` (unlimited — let SCP/OTB decide)
6. Check **Use cross-validation** if not doing manual split
7. Set output filename: `classification_RF.tif`
8. Click **RUN**

> **Expected runtime**: 2–10 minutes depending on AOI size and machine specs.

#### 5.3 Run SVM Classification (via SCP)

1. In the same **Classification** tab
2. Change **Algorithm**: `Support Vector Machine (SVM)`
3. Set parameters:
   - **Kernel type**: `Radial Basis Function (RBF)`
   - **C (Cost)**: `100`
   - **Gamma**: `0.1`
   - *(These are reasonable defaults; you can tune them later)*
4. Set output filename: `classification_SVM.tif`
5. Click **RUN**

> **Expected runtime**: 5–20 minutes (SVM is slower than RF for large datasets)

#### 5.4 Alternative: Run Classifications via OTB in QGIS Processing Toolbox

If SCP classification doesn't work on your system, use OTB directly:

**Via Processing Toolbox** (QGIS → Processing → Toolbox → search "OTB"):

For **Random Forest**:
```
Tool: OTB → Learning → TrainVectorClassifier
- Input samples: your training shapefile
- Input features: band names
- Classifier: rf
- rf.nbtrees: 100
- Output model: rf_model.yaml
```

```
Tool: OTB → Learning → ImageClassifier  
- Input image: sentinel2_stack.tif
- Input model: rf_model.yaml
- Output image: classification_RF.tif
```

For **SVM**, repeat with `classifier: libsvm`

#### 5.5 Style the Classification Output

1. Right-click `classification_RF.tif` → **Properties** → **Symbology**
2. Set **Render type**: Paletted/Unique values
3. Click **Classify**
4. Assign the class colors from your table in Phase 4
5. Rename each class label appropriately
6. Repeat for `classification_SVM.tif`

---

### Phase 6: Accuracy Assessment & Comparison

#### 6.1 Run Accuracy Assessment in SCP

1. Open **SCP** → **Postprocessing** → **Accuracy**
2. Under **Classification**, load `classification_RF.tif`
3. Under **Reference**, load your test samples (exported from SCP as a raster, or use your `testing_30pct` samples)
4. Click **Calculate accuracy**

SCP will produce:
- **Confusion matrix** (actual vs. predicted class counts)
- **Overall Accuracy** (OA) — percentage of correctly classified pixels
- **Kappa Coefficient** (κ) — accuracy adjusted for chance agreement
- **Producer's Accuracy** (PA) — per-class recall
- **User's Accuracy** (UA) — per-class precision

Save the results: **Export** → Save as `accuracy_RF.csv`

Repeat for `classification_SVM.tif` → Save as `accuracy_SVM.csv`

#### 6.2 Compare Classifiers in Python

```python
# compare_classifiers.py
# Summarizes and compares RF vs SVM accuracy metrics

import pandas as pd

# ── Load accuracy reports ─────────────────────────────────────────────────────
# (Adjust column names to match SCP's export format)

rf_acc  = pd.read_csv("accuracy_RF.csv")
svm_acc = pd.read_csv("accuracy_SVM.csv")

# ── Extract key metrics ───────────────────────────────────────────────────────
# SCP exports Overall Accuracy and Kappa in a summary row
# Adjust indexing based on your actual SCP output format

def extract_summary(df, classifier_name):
    """Extract OA, Kappa, and per-class UA/PA from SCP accuracy table."""
    summary = {
        "Classifier":       classifier_name,
        "Overall Accuracy": None,
        "Kappa":            None,
    }
    # SCP typically puts OA and Kappa in the bottom rows of the matrix
    # Inspect your CSV to find the correct row/column names
    # Example extraction (adjust as needed):
    try:
        summary["Overall Accuracy"] = float(
            df[df.iloc[:, 0].str.contains("Overall", na=False)].iloc[0, 1]
        )
        summary["Kappa"] = float(
            df[df.iloc[:, 0].str.contains("Kappa", na=False)].iloc[0, 1]
        )
    except Exception as e:
        print(f"Could not parse summary metrics for {classifier_name}: {e}")
        print("Please check your CSV format and adjust extraction logic.")
    return summary

rf_summary  = extract_summary(rf_acc,  "Random Forest")
svm_summary = extract_summary(svm_acc, "SVM")

comparison = pd.DataFrame([rf_summary, svm_summary])
print("\n=== Classifier Comparison ===")
print(comparison.to_string(index=False))

# ── Interpret results ─────────────────────────────────────────────────────────
print("\n=== Interpretation Guide ===")
print("Overall Accuracy > 85%  → Acceptable for publication")
print("Kappa > 0.80            → Strong agreement")
print("Kappa 0.60–0.80         → Moderate agreement — consider resampling weak classes")
print("Kappa < 0.60            → Poor — revisit training samples")
```

#### 6.3 Interpret Your Results

Use this decision framework after reviewing accuracy:

```
Is Overall Accuracy > 80%?
│
├── YES → Proceed to write-up
│         Note which classifier performed better and by how much
│
└── NO  → Diagnose the problem:
          │
          ├── Which classes have lowest Producer's Accuracy?
          │   → Add more training samples for those classes
          │
          ├── Are spectrally similar classes confused?
          │   → Consider merging them or adding discriminating indices
          │
          └── Is overall sample count low (<500 total)?
              → Collect more samples and re-run
```

#### 6.4 Visual QA — Spot Check the Classification Map

Don't rely on numbers alone. Visually inspect your classification:

1. Toggle between the classified raster and the original false-color composite
2. Zoom into known locations (e.g., a large water body, a forested area, an urban center)
3. Note any obvious misclassifications — these often reveal systematic issues (e.g., shadows classified as water)
4. Document 3–5 specific examples of correct and incorrect classification for your write-up

---

## 4. Validation

### ✅ Checklist — Have You Successfully Completed the Exercise?

Work through this checklist before writing up your results:

**Data Preparation**
- [ ] Sentinel-2 image downloaded for your AOI with <10% cloud cover
- [ ] Image loaded in QGIS with correct CRS
- [ ] At least 3 spectral indices calculated and stacked with source bands
- [ ] False color composite visualized and interpreted

**Training Samples**
- [ ] Minimum 5 land cover classes defined with clear descriptions
- [ ] At least 150 training pixels per class collected
- [ ] Jeffries-Matusita separability distances all > 1.5
- [ ] Training and test sets split (70/30)

**Classification**
- [ ] Random Forest classification completed successfully — output raster saved
- [ ] SVM classification completed successfully — output raster saved
- [ ] Both outputs styled with meaningful class colors

**Accuracy Assessment**
- [ ] Confusion matrix generated for both RF and SVM
- [ ] Overall Accuracy and Kappa extracted for both classifiers
- [ ] At least one classifier achieves OA > 80% / Kappa > 0.70
- [ ] Visual spot-check performed and documented

**Deliverable**
- [ ] "The Build" post draft written (see template below)

### Expected Benchmark Metrics

| Scenario | Overall Accuracy | Kappa |
|---|---|---|
| Excellent (5 simple classes, good training) | > 92% | > 0.90 |
| Good (5–7 classes, typical training) | 85–92% | 0.80–0.90 |
| Acceptable (complex scene, first attempt) | 78–85% | 0.70–0.80 |
| Needs work | < 78% | < 0.70 |

---

## 5. Write the "The Build" Post Draft

Use this template for your Globe & Atlas "The Build" post:

```markdown
# How I Mapped [Land Cover Topic] Using Sentinel-2, QGIS, and Machine Learning

*The Build | [Your Name] | [Date]*

---

## The Problem

[2–3 sentences: What geographic/environmental question motivated this map?
Why does land cover change matter in this region?]

## The Data

- **Satellite**: Sentinel-2 Level-2A
- **Scene date**: [your date range]
- **Location**: [your AOI]
- **Bands used**: [list your 8 bands + indices]
- **Source**: Sentinel Hub API

## The Method

I used two supervised classification algorithms:

**Random Forest** — an ensemble of [100] decision trees that votes on
the most likely class for each pixel. Fast to train, robust to noisy
training data.

**Support Vector Machine (SVM)** — finds the optimal hyperplane
separating classes in feature space. Slower to train but often more
precise with limited training data.

Training samples were collected manually in QGIS using the
Semi-Automatic Classification Plugin (SCP), with [total N] pixels
across [N] classes.

## The Results

| Classifier | Overall Accuracy | Kappa |
|---|---|---|
| Random Forest | [X]% | [X] |
| SVM | [X]% | [X] |

[Winner] performed better overall, particularly for [class name]
which had [observation].

The biggest challenge was distinguishing [class A] from [class B] —
both show similar NIR reflectance values. Adding [index] helped
separate them.

## What This Reveals

[2–3 sentences connecting your map to the Globe & Atlas editorial angle:
What story does this classification tell? What would a journalist or
reader take away from looking at your output map?]

## The Code & Data

Full scripts: [GitHub link]
Tutorial source: [YouTube link]

---
*Built with QGIS 3.28, SCP 8.x, Sentinel Hub API*
```

---

## 6. Next Steps

### Immediate Improvements to This Workflow

1. **Hyperparameter tuning** — Use scikit-learn's `GridSearchCV` to find optimal SVM `C` and `gamma` values, or RF `n_estimators` and `max_features`
2. **Add SAR data** — Fuse Sentinel-1 SAR (radar) bands with Sentinel-2 optical bands to better distinguish classes obscured by cloud or similar spectral signatures
3. **Temporal stack** — Stack multi-date Sentinel-2 images to capture seasonal vegetation patterns, dramatically improving crop type mapping accuracy
4. **Object-based classification** — Try QGIS/OTB's segmentation tools to classify image segments rather than individual pixels, reducing salt-and-pepper noise

### Extend to Related Globe & Atlas Stories

| Next Article Topic | Classification Extension |
|---|---|
| "The Last Wetlands of [Region]" | Add wetland change detection between two dates |
| "Urban Heat Island" | Combine land cover map with Landsat LST |
| "Deforestation Rate Report" | Binary forest/non-forest for two years, calculate area change |
| "Agricultural Water Use" | Add Sentinel-2 LAI product + classified cropland area |

### Deepen Your Technical Skills

- **Google Earth Engine** — Run the same SVM/RF workflow at continental scale without local computation: [developers.google.com/earth-engine](https://developers.google.com/earth-engine)
- **Python end-to-end** — Replace QGIS GUI with a full Python pipeline using `rasterio`, `scikit-learn`, and `geopandas` for reproducible, scriptable classification
- **Deep learning** — Explore U-Net semantic segmentation for higher-accuracy land cover mapping: see the [TorchGeo library](https://torchgeo.readthedocs.io)

### Publish and Build Your Portfolio

1. Push all scripts and the training sample file to a public GitHub repo
2. Export your final classification map as a PNG at 300 DPI for the article
3. Consider contributing your training samples to OpenStreetMap-based land cover initiatives
4. Share your "The Build" post on LinkedIn tagging #RemoteSensing #Sentinel2 #GIS

---

## Appendix: Quick Reference — Band Indices Cheat Sheet

| Index | Formula (using our band numbering) | What It Highlights |
|---|---|---|
| NDVI | (B6−B3)/(B6+B3) | Vegetation density |
| NDWI