"""Heat layer, step 7: UTCI per street segment and time window.
Run from the repo root:  python code/4_hazards/heat/7_segment_heat.py video5
"""
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import Affine

sys.path.insert(0, "code")
import paths

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
BUFFER_M = 5  # street pixels within 5 m of the segment line
# hour stamps are the END of each hour: morning = 6-10 am, midday = 10 am-3 pm, afternoon = 3-7 pm
BINS = {"morning": range(7, 11), "midday": range(11, 16), "afternoon": range(16, 20)}

label = sys.argv[1]
utci_folder = paths.where(label, "outputs") / "heat_run" / "output" / "utci"

# 1. load the hourly UTCI maps
hourly = {}
for f in sorted(utci_folder.glob("utci_*.tif")):
    hour = int(f.stem[-4:-2])
    with rasterio.open(f) as src:
        hourly[hour] = src.read(1)
        transform, crs = src.transform, src.crs
print(f"{len(hourly)} hourly maps loaded")

# 2. per pixel, per time window: mean and 95th percentile over the hours
layers = {}
for name, hours in BINS.items():
    cube = np.stack([hourly[h] for h in hours])
    layers[f"{name}_mean"] = np.nanmean(cube, axis=0)
    layers[f"{name}_p95"] = np.percentile(cube, 95, axis=0)
rows_n, cols_n = layers["morning_mean"].shape

# 3. street pixels only: pixels where the building layer says "no building"
with rasterio.open(FOLDER + r"\nanganallur_buildings_2023.tif") as src:
    street = src.read(3) < 0.5

# 4. average each layer over the street pixels next to every segment
segs = gpd.read_file(FOLDER + r"\streets_nanganallur.gpkg", layer="segments")
assert segs.crs == crs, "segments and heat maps are in different map systems"
inverse = ~transform
out = []
for seg in segs.itertuples():
    zone = seg.geometry.buffer(BUFFER_M, cap_style="flat")
    minx, miny, maxx, maxy = zone.bounds
    c0, r0 = inverse * (minx, maxy)
    c1, r1 = inverse * (maxx, miny)
    r0, r1 = max(int(np.floor(r0)), 0), min(int(np.ceil(r1)), rows_n)
    c0, c1 = max(int(np.floor(c0)), 0), min(int(np.ceil(c1)), cols_n)
    row = {"segment_id": seg.segment_id}
    if r1 <= r0 or c1 <= c0:
        out.append(row)
        continue
    window_transform = transform * Affine.translation(c0, r0)
    mask = rasterize([(zone, 1)], out_shape=(r1 - r0, c1 - c0),
                     transform=window_transform, fill=0).astype(bool)
    mask &= street[r0:r1, c0:c1]
    row["street_pixels"] = int(mask.sum())
    for key, layer in layers.items():
        values = layer[r0:r1, c0:c1][mask]
        values = values[np.isfinite(values)]
        row[key] = round(float(values.mean()), 2) if len(values) else np.nan
    out.append(row)

table = pd.DataFrame(out)
target = paths.where(label, "outputs") / "heat_by_segment.csv"
table.to_csv(target, index=False)
print(f"saved {len(table)} segments to {target}")
print(table.describe().round(1).T)