"""Heat layer, step 10: tree cover seen by the model on each route segment.
Run from the repo root:  python code/4_hazards/heat/10_route_canopy.py video5
"""
import sys

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import rasterize

sys.path.insert(0, "code")
import paths

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
BUFFER_M = 5

label = sys.argv[1]
route = pd.read_csv(paths.where(label, "data") / "route_segments.csv")
heat = pd.read_csv(paths.where(label, "outputs") / "heat_by_segment.csv")
seg = gpd.read_file(FOLDER + r"\streets_nanganallur.gpkg", layer="segments")
seg = seg.merge(route, on="segment_id").merge(
    heat[["segment_id", "midday_mean"]], on="segment_id").sort_values("order")

with rasterio.open(FOLDER + r"\nanganallur_canopy.tif") as c:
    canopy, transform = c.read(1), c.transform
with rasterio.open(FOLDER + r"\nanganallur_buildings_2023.tif") as b:
    street = b.read(3) < 0.5

rows = []
for _, r in seg.iterrows():
    shape = [(r.geometry.buffer(BUFFER_M, cap_style="flat"), 1)]
    mask = rasterize(shape, out_shape=canopy.shape, transform=transform,
                     fill=0, dtype="uint8") == 1
    m = mask & street
    rows.append({"order": r["order"], "segment_id": r.segment_id,
                 "length_m": round(r.length_m, 1),
                 "canopy_pct": round(100 * (canopy[m] > 0).mean()),
                 "midday_mean": round(r.midday_mean, 1)})
print(pd.DataFrame(rows).to_string(index=False))