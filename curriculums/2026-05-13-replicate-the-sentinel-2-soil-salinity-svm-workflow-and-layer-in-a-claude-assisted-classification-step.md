# Replicate the Sentinel-2 Soil Salinity SVM Workflow with Claude-Assisted Classification

## A Complete Hands-On Curriculum for AI-Augmented Supervised Remote Sensing

---

## 1. Introduction & Context

### What You're Building

This tutorial walks you through replicating a professional supervised classification pipeline for **soil salinity mapping** using Sentinel-2 multispectral imagery — then extending it with an AI layer that would have been impossible a few years ago: using the **Claude API to auto-generate legend descriptions and anomaly flags** from your output raster.

The result is a hybrid, publishable workflow that sits at the intersection of:

- **Classical machine learning** (SVM, Random Forest) applied to satellite imagery
- **Modern GIS tooling** (QGIS, rasterio, geopandas)
- **AI augmentation** (Claude API) for interpretation and reporting

### Why This Matters

Soil salinity is a critical land degradation indicator affecting agricultural productivity worldwide. Traditional field surveys are expensive and spatially sparse. Sentinel-2's free, 10–20m resolution multispectral bands — particularly in the red-edge and SWIR ranges — carry strong spectral signatures for salt-affected soils, making satellite-based supervised classification both practical and impactful.

More broadly, this workflow is a template. Swap the training labels and you can classify land cover, flood extent, burned area, or crop type using the same stack.

### The Claude Augmentation Layer

The novel piece you're adding is a **post-classification AI step** where Claude:

1. Reads your classified raster statistics
2. Auto-generates human-readable legend descriptions per class
3. Flags spatial anomalies (e.g., unexpected salinity patches near irrigation canals)
4. Drafts a plain-language summary suitable for a GIS audience post

This is the "AI-augmented supervised classification" angle that makes this publishable as a **Build post**.

---

## 2. Prerequisites

### Knowledge Requirements

| Skill | Level Needed |
|---|---|
| Python (numpy, pandas) | Intermediate |
| QGIS basic navigation | Beginner–Intermediate |
| Remote sensing concepts (bands, indices) | Basic familiarity |
| REST APIs / JSON | Basic |
| Git / command line | Basic |

### Software & Accounts

```
✅ QGIS 3.28+ (LTR recommended) — https://qgis.org
✅ Python 3.9+ with the following packages
✅ Anthropic API key — https://console.anthropic.com
✅ ESA Copernicus Open Access Hub account (free) — https://scihub.copernicus.eu
   OR Copernicus Data Space Ecosystem — https://dataspace.copernicus.eu
```

### Python Environment Setup

```bash
# Create a dedicated conda environment (recommended)
conda create -n salinity_ml python=3.11
conda activate salinity_ml

# Core geospatial stack
pip install rasterio geopandas shapely fiona pyproj

# Machine learning
pip install scikit-learn imbalanced-learn joblib

# Visualization & reporting
pip install matplotlib seaborn plotly folium

# Claude API
pip install anthropic

# Utilities
pip install numpy pandas tqdm jupyter notebook python-dotenv

# Optional: QGIS Python bindings for headless scripting
# (usually comes with QGIS installation, add to PYTHONPATH)
```

### Data Requirements

You will need:

1. **Sentinel-2 L2A scene** (atmospherically corrected, surface reflectance)
   - Recommended: A scene over an arid/semi-arid agricultural region (Nile Delta, Indus Plain, Central Asia, Imperial Valley)
   - Bands needed: B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12
   - Time of year: Dry season preferred (less vegetation confusion)

2. **Training samples** (you'll create these in QGIS):
   - Minimum 50 points per class
   - Classes: `non_saline`, `slightly_saline`, `moderately_saline`, `highly_saline`, `water`, `urban`, `vegetation`

3. **Reference data** (optional but recommended):
   - EC (electrical conductivity) field measurements
   - Existing soil maps for validation

### Project Directory Structure

```
salinity_project/
├── data/
│   ├── raw/
│   │   └── S2A_MSIL2A_*.SAFE/          # Downloaded Sentinel-2 scene
│   ├── processed/
│   │   ├── stacked_bands.tif           # Band stack output
│   │   └── indices.tif                 # Spectral indices
│   ├── training/
│   │   ├── training_points.gpkg        # QGIS training samples
│   │   └── training_data.csv           # Extracted pixel values
│   └── outputs/
│       ├── svm_classified.tif
│       ├── rf_classified.tif
│       └── combined_classified.tif
├── models/
│   ├── svm_model.pkl
│   └── rf_model.pkl
├── reports/
│   ├── classification_report.txt
│   ├── claude_legend.json
│   └── build_post_draft.md
├── notebooks/
│   └── salinity_workflow.ipynb
├── scripts/
│   ├── 01_prepare_bands.py
│   ├── 02_extract_training.py
│   ├── 03_train_classify.py
│   ├── 04_validate.py
│   └── 05_claude_augment.py
├── .env                                # API keys (never commit)
└── requirements.txt
```

---

## 3. Step-by-Step Guide

### Phase 1: Data Acquisition & Preparation

#### Step 1.1 — Download Your Sentinel-2 Scene

Navigate to the **Copernicus Data Space** browser:

```
https://browser.dataspace.copernicus.eu/
```

**Search parameters:**
- **Dataset:** SENTINEL-2 → L2A
- **Cloud coverage:** < 10%
- **Date range:** Dry season months for your target region
- **Tile:** Use the Sentinel-2 tile grid to find your area

Download the full `.SAFE` folder. It will be ~800MB–1.2GB.

**Alternative: Use the `sentinelsat` Python library**

```python
# scripts/download_scene.py
from sentinelsat import SentinelAPI
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

api = SentinelAPI(
    os.getenv('COPERNICUS_USER'),
    os.getenv('COPERNICUS_PASSWORD'),
    'https://apihub.copernicus.eu/apihub'
)

# Example: Nile Delta, Egypt — adjust to your area
footprint = 'POLYGON((30.5 30.0, 32.0 30.0, 32.0 31.5, 30.5 31.5, 30.5 30.0))'

products = api.query(
    footprint,
    date=('20230601', '20230930'),
    platformname='Sentinel-2',
    processinglevel='Level-2A',
    cloudcoverpercentage=(0, 10)
)

# Download the least cloudy scene
products_df = api.to_dataframe(products)
best = products_df.sort_values('cloudcoverpercentage').iloc[0]
print(f"Downloading: {best['title']}")
api.download(best.name, directory_path='data/raw/')
```

#### Step 1.2 — Stack Sentinel-2 Bands

Sentinel-2 L2A delivers bands as separate `.jp2` files at different resolutions. This script resamples everything to 10m and creates a single multi-band GeoTIFF.

```python
# scripts/01_prepare_bands.py
import rasterio
from rasterio.enums import Resampling
from rasterio.merge import merge
import numpy as np
import glob
import os
from pathlib import Path

def find_band_files(safe_dir: str) -> dict:
    """Find Sentinel-2 band files in a .SAFE directory."""
    
    # Band mapping: band_name -> (filename_pattern, native_resolution)
    bands_10m = {
        'B02': '*B02_10m.jp2',  # Blue
        'B03': '*B03_10m.jp2',  # Green
        'B04': '*B04_10m.jp2',  # Red
        'B08': '*B08_10m.jp2',  # NIR
    }
    bands_20m = {
        'B05': '*B05_20m.jp2',  # Red Edge 1
        'B06': '*B06_20m.jp2',  # Red Edge 2
        'B07': '*B07_20m.jp2',  # Red Edge 3
        'B8A': '*B8A_20m.jp2',  # Red Edge 4
        'B11': '*B11_20m.jp2',  # SWIR 1
        'B12': '*B12_20m.jp2',  # SWIR 2
    }
    
    found = {}
    for band_name, pattern in {**bands_10m, **bands_20m}.items():
        matches = glob.glob(os.path.join(safe_dir, '**', pattern), recursive=True)
        if matches:
            found[band_name] = matches[0]
        else:
            print(f"⚠️  Could not find {band_name}")
    
    return found

def stack_bands(safe_dir: str, output_path: str) -> None:
    """Stack all bands into a single GeoTIFF at 10m resolution."""
    
    band_files = find_band_files(safe_dir)
    band_order = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12']
    
    print("📦 Stacking bands...")
    
    # Use B02 (10m) as reference for spatial extent and CRS
    with rasterio.open(band_files['B02']) as ref:
        ref_meta = ref.meta.copy()
        ref_transform = ref.transform
        ref_crs = ref.crs
        ref_width = ref.width
        ref_height = ref.height
    
    ref_meta.update({
        'count': len(band_order),
        'dtype': 'float32',
        'driver': 'GTiff',
        'compress': 'lzw',
        'nodata': -9999
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with rasterio.open(output_path, 'w', **ref_meta) as dst:
        for i, band_name in enumerate(band_order, 1):
            filepath = band_files[band_name]
            print(f"  Processing band {band_name} ({i}/{len(band_order)})...")
            
            with rasterio.open(filepath) as src:
                # Resample 20m bands to 10m if needed
                if src.res[0] != 10.0:
                    data = src.read(
                        1,
                        out_shape=(ref_height, ref_width),
                        resampling=Resampling.bilinear
                    )
                else:
                    data = src.read(1)
                
                # Convert DN to surface reflectance (divide by 10000)
                data = data.astype('float32') / 10000.0
                data[data < 0] = -9999  # Handle nodata
                
                dst.write(data, i)
    
    print(f"✅ Band stack saved to: {output_path}")
    print(f"   Bands: {band_order}")
    print(f"   Shape: {ref_height} x {ref_width} x {len(band_order)}")

def compute_spectral_indices(stack_path: str, output_path: str) -> None:
    """Compute spectral indices relevant to soil salinity."""
    
    print("📐 Computing spectral indices...")
    
    with rasterio.open(stack_path) as src:
        # Read relevant bands (1-indexed: B02=1, B03=2, B04=3, B05=4, B06=5, 
        #                                  B07=6, B08=7, B8A=8, B11=9, B12=10)
        B02 = src.read(1).astype('float32')  # Blue
        B03 = src.read(2).astype('float32')  # Green
        B04 = src.read(3).astype('float32')  # Red
        B08 = src.read(7).astype('float32')  # NIR
        B11 = src.read(9).astype('float32')  # SWIR1
        B12 = src.read(10).astype('float32') # SWIR2
        
        meta = src.meta.copy()
    
    # Avoid division by zero
    eps = 1e-10
    
    # NDVI - Normalized Difference Vegetation Index
    ndvi = (B08 - B04) / (B08 + B04 + eps)
    
    # NDSI - Normalized Difference Salinity Index
    ndsi = (B04 - B11) / (B04 + B11 + eps)
    
    # SI1 - Salinity Index 1
    si1 = np.sqrt(np.abs(B04 * B11))
    
    # SI2 - Salinity Index 2 (Douaoui et al.)
    si2 = np.sqrt(np.abs(B03 * B04))
    
    # SI3 - Salinity Index 3
    si3 = np.sqrt(np.abs(B02 * B04))
    
    # NDWI - Normalized Difference Water Index (for water masking)
    ndwi = (B03 - B08) / (B03 + B08 + eps)
    
    # EVI - Enhanced Vegetation Index
    evi = 2.5 * ((B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1 + eps))
    
    indices = [ndvi, ndsi, si1, si2, si3, ndwi, evi]
    index_names = ['NDVI', 'NDSI', 'SI1', 'SI2', 'SI3', 'NDWI', 'EVI']
    
    meta.update({
        'count': len(indices),
        'dtype': 'float32',
        'compress': 'lzw'
    })
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        for i, (index_data, name) in enumerate(zip(indices, index_names), 1):
            # Clip to reasonable range
            index_data = np.clip(index_data, -2, 2)
            dst.write(index_data, i)
    
    print(f"✅ Indices saved: {index_names}")
    print(f"   Output: {output_path}")

if __name__ == '__main__':
    import sys
    
    safe_dir = sys.argv[1] if len(sys.argv) > 1 else 'data/raw/S2A_MSIL2A_sample.SAFE'
    
    stack_output = 'data/processed/stacked_bands.tif'
    indices_output = 'data/processed/indices.tif'
    
    stack_bands(safe_dir, stack_output)
    compute_spectral_indices(stack_output, indices_output)
```

Run it:

```bash
python scripts/01_prepare_bands.py data/raw/S2A_MSIL2A_20230815T083601_N0509_R064_T36RUU_20230815T124301.SAFE
```

---

### Phase 2: Training Sample Collection in QGIS

#### Step 2.1 — Load Your Data in QGIS

1. Open QGIS
2. **Layer → Add Layer → Add Raster Layer**
3. Navigate to `data/processed/stacked_bands.tif` and load it
4. In the **Layer Styling panel**, set:
   - Band rendering: **Multiband color**
   - Red: Band 3 (B04 — Red)
   - Green: Band 7 (B08 — NIR)
   - Blue: Band 2 (B03 — Green)
   - This gives you a **False Color Composite** (vegetation = red, soil = cyan/blue-green)

5. Load the indices layer too (`data/processed/indices.tif`)

#### Step 2.2 — Create Training Points

1. **Layer → Create Layer → New GeoPackage Layer**
   - Database: `data/training/training_points.gpkg`
   - Table name: `training_samples`
   - Geometry type: **Point**
   - CRS: Match your raster CRS
   - Add a field: `class_id` (Integer)
   - Add a field: `class_name` (Text, 50 chars)
   - Add a field: `notes` (Text, 200 chars)

2. **Toggle editing** on the new layer (pencil icon)

3. Use **Add Point Feature** to digitize training samples

**Class scheme:**

| class_id | class_name | Visual signature in false color |
|---|---|---|
| 1 | non_saline | Dark tones, may have vegetation |
| 2 | slightly_saline | Light brown, scattered white patches |
| 3 | moderately_saline | White/grey surface crust |
| 4 | highly_saline | Bright white, often near drainage |
| 5 | water | Dark blue/black |
| 6 | urban | Magenta/bright varied tones |
| 7 | vegetation | Bright red (false color) |

**Best practices:**
- Aim for **50–100 points per class minimum**
- Distribute samples across the full scene extent
- Use multiple spectral windows and zoom levels
- Cross-reference with Google Satellite (add via **XYZ Tiles** in Browser panel):
  `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`

4. **Save the layer** when done

#### Step 2.3 — Verify Sample Distribution

In QGIS:
1. Right-click `training_samples` → **Open Attribute Table**
2. Check class distribution
3. **Vector → Analysis → Basic Statistics for Fields** (check class_id distribution)

---

### Phase 3: Extract Training Data

#### Step 3.1 — Extract Pixel Values at Training Points

```python
# scripts/02_extract_training.py
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.sample import sample_gen
from pathlib import Path

def extract_pixel_values(
    raster_path: str,
    points_path: str,
    layer_name: str = 'training_samples',
    band_prefix: str = 'band'
) -> pd.DataFrame:
    """Extract raster values at training point locations."""
    
    print(f"📍 Extracting pixel values from {raster_path}")
    
    # Load training points
    gdf = gpd.read_file(points_path, layer=layer_name)
    print(f"   Loaded {len(gdf)} training points")
    print(f"   Classes: {gdf['class_name'].value_counts().to_dict()}")
    
    with rasterio.open(raster_path) as src:
        # Reproject points to raster CRS if needed
        if gdf.crs != src.crs:
            print(f"   Reprojecting from {gdf.crs} to {src.crs}")
            gdf = gdf.to_crs(src.crs)
        
        # Extract coordinates
        coords = [(geom.x, geom.y) for geom in gdf.geometry]
        
        # Sample raster at all coordinates
        values = list(src.sample(coords))
        values_array = np.array(values)
        
        # Create column names
        n_bands = src.count
        col_names = [f'{band_prefix}_{i+1}' for i in range(n_bands)]
    
    # Combine with metadata
    pixel_df = pd.DataFrame(values_array, columns=col_names)
    
    result_df = pd.concat([
        gdf[['class_id', 'class_name']].reset_index(drop=True),
        pixel_df
    ], axis=1)
    
    # Remove nodata points
    nodata_mask = (values_array == -9999).any(axis=1)
    result_df = result_df[~nodata_mask]
    print(f"   Removed {nodata_mask.sum()} nodata points")
    
    return result_df

def build_feature_matrix(
    stack_path: str,
    indices_path: str,
    points_path: str,
    output_csv: str
) -> pd.DataFrame:
    """Build complete feature matrix combining bands and indices."""
    
    # Extract band values
    bands_df = extract_pixel_values(
        stack_path, points_path, 
        band_prefix='b'
    )
    
    # Extract index values
    indices_df = extract_pixel_values(
        indices_path, points_path,
        band_prefix='idx'
    )
    
    # Rename index columns to be descriptive
    index_names = ['NDVI', 'NDSI', 'SI1', 'SI2', 'SI3', 'NDWI', 'EVI']
    indices_df = indices_df.rename(columns={
        f'idx_{i+1}': name for i, name in enumerate(index_names)
    })
    
    # Combine (drop duplicate metadata columns from indices)
    feature_cols = [c for c in indices_df.columns if c not in ['class_id', 'class_name']]
    combined = pd.concat([
        bands_df,
        indices_df[feature_cols]
    ], axis=1)
    
    # Band column names
    band_names = ['B02_Blue', 'B03_Green', 'B04_Red', 'B05_RE1', 
                  'B06_RE2', 'B07_RE3', 'B08_NIR', 'B8A_RE4', 
                  'B11_SWIR1', 'B12_SWIR2']
    rename_map = {f'b_{i+1}': name for i, name in enumerate(band_names)}
    combined = combined.rename(columns=rename_map)
    
    # Save
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_csv, index=False)
    
    print(f"\n✅ Feature matrix saved: {output_csv}")
    print(f"   Shape: {combined.shape}")
    print(f"\n📊 Class distribution:")
    print(combined['class_name'].value_counts())
    
    return combined

if __name__ == '__main__':
    df = build_feature_matrix(
        stack_path='data/processed/stacked_bands.tif',
        indices_path='data/processed/indices.tif',
        points_path='data/training/training_points.gpkg',
        output_csv='data/training/training_data.csv'
    )
```

```bash
python scripts/02_extract_training.py
```

---

### Phase 4: Train & Apply SVM and Random Forest Classifiers

```python
# scripts/03_train_classify.py
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds
import joblib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, cohen_kappa_score
)
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance
import seaborn as sns
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================
TRAINING_CSV = 'data/training/training_data.csv'
STACK_PATH = 'data/processed/stacked_bands.tif'
INDICES_PATH = 'data/processed/indices.tif'
OUTPUT_DIR = 'data/outputs'
MODEL_DIR = 'models'
REPORT_DIR = 'reports'

# Class color mapping for visualization
CLASS_COLORS = {
    1: '#4CAF50',  # non_saline - green
    2: '#FFEB3B',  # slightly_saline - yellow
    3: '#FF9800',  # moderately_saline - orange
    4: '#F44336',  # highly_saline - red
    5: '#2196F3',  # water - blue
    6: '#9E9E9E',  # urban - grey
    7: '#1B5E20',  # vegetation - dark green
}

CLASS_NAMES = {
    1: 'Non-Saline',
    2: 'Slightly Saline',
    3: 'Moderately Saline',
    4: 'Highly Saline',
    5: 'Water',
    6: 'Urban',
    7: 'Vegetation',
}

# ============================================================
# DATA PREPARATION
# ============================================================
def load_training_data(csv_path: str):
    """Load and prepare training data."""
    
    df = pd.read_csv(csv_path)
    
    # Feature columns (all except class metadata)
    feature_cols = [c for c in df.columns if c not in ['class_id', 'class_name']]
    
    X = df[feature_cols].values
    y = df['class_id'].values
    
    print(f"📊 Training data loaded:")
    print(f"   Features: {feature_cols}")
    print(f"   Samples: {len(X)}")
    print(f"   Classes: {dict(zip(*np.unique(y, return_counts=True)))}")
    
    return X, y, feature_cols

# ============================================================
# MODEL TRAINING
# ============================================================
def train_svm(X_train, y_train) -> Pipeline:
    """Train SVM classifier with RBF kernel."""
    
    print("\n🔧 Training SVM...")
    
    svm_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(
            kernel='rbf',
            C=100,
            gamma='scale',
            probability=True,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        ))
    ])
    
    svm_pipeline.fit(X_train, y_train)
    print("   ✅ SVM training complete")
    
    return svm_pipeline

def train_random_forest(X_train, y_train) -> RandomForestClassifier:
    """Train Random Forest classifier."""
    
    print("\n🌲 Training Random Forest...")
    
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        oob_score=True
    )
    
    rf_model.fit(X_train, y_train)
    print(f"   OOB Score: {rf_model.oob_score_:.4f}")
    print("   ✅ Random Forest training complete")
    
    return rf_model

def evaluate_models(models: dict, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    """Evaluate all models and return metrics."""
    
    results = {}
    
    for name, model in models.items():
        print(f"\n📈 Evaluating {name}:")
        
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        kappa = cohen_kappa_score(y_test, y_pred)
        
        print(f"   Overall Accuracy: {acc:.4f}")
        print(f"   Cohen's Kappa: {kappa:.4f}")
        
        report = classification_report(
            y_test, y_pred,
            target_names=[CLASS_NAMES.get(i, str(i)) for i in sorted(np.unique(y_test))]
        )
        print(f"\n{report}")
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, 
                                     np.vstack([X_test, X_test[:50]]),  # Small CV on test
                                     np.concatenate([y_test, y_test[:50]]),
                                     cv=cv, scoring='accuracy')
        
        results[name] = {
            'accuracy': acc,
            'kappa': kappa,
            'report': report,
            'y_pred': y_pred,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    return results

# ============================================================
# FULL SCENE CLASSIFICATION
# ============================================================
def classify_raster(
    model,
    stack_path: str,
    indices_path: str,
    output_path: str,
    batch_size: int = 100000
) -> np.ndarray:
    """Apply classifier to full scene, processing in batches."""
    
    print(f"\n🗺️  Classifying full scene...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with rasterio.open(stack_path) as stack_src, \
         rasterio.open(indices_path) as idx_src:
        
        # Read all bands
        print("   Reading band stack...")
        bands = stack_src.read().astype('float32')  # (10, H, W)
        
        print("   Reading indices...")
        indices = idx_src.read().astype('float32')  # (7, H, W)
        
        H, W = bands.shape[1], bands.shape[2]
        meta = stack_src.meta.copy()
        
        # Stack features: (17, H, W) -> (H*W, 17)
        all_features = np.vstack([bands, indices])  # (17, H, W)
        n_bands_total = all_features.shape[0]
        
        # Reshape to pixels
        features_2d = all_features.reshape(n_bands_total, -1).T  # (H*W, 17)
        
        # Identify valid pixels (not nodata)
        valid_mask = ~(features_2d == -9999).any(axis=1)
        n_valid = valid_mask.sum()
        
        print(f"   Total pixels: {H*W:,}")
        print(f"   Valid pixels: {n_valid:,} ({100*n_valid/(H*W):.1f}%)")
        
        # Initialize output
        classified = np.zeros(H * W, dtype='uint8')
        
        # Classify in batches
        valid_indices = np.where(valid_mask)[0]
        n_batches = (n_valid + batch_size - 1) // batch_size
        
        print(f"