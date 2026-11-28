"""Heat layer, step 9: heat of the route of one video.
Run from the repo root:  python code/4_hazards/heat/9_route_heat.py video5
Reads data/.../route_segments.csv and outputs/.../heat_by_segment.csv.
"""
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, "code")
import paths

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
WINDOWS = ["morning", "midday", "afternoon"]

label = sys.argv[1]
route = pd.read_csv(paths.where(label, "data") / "route_segments.csv")
heat = pd.read_csv(paths.where(label, "outputs") / "heat_by_segment.csv")
seg = gpd.read_file(FOLDER + r"\streets_nanganallur.gpkg", layer="segments")
seg = seg[["segment_id", "name", "highway", "length_m"]]

table = route.merge(seg, on="segment_id", how="left")
table = table.merge(heat, on="segment_id", how="left").sort_values("order")
out = paths.where(label, "outputs") / "route_heat.csv"
table.to_csv(out, index=False)

full = table[table.coverage == "full"]
print("segments:", len(table), "| route length:", round(table.length_m.sum(), 1), "m",
      "| full segments only:", round(full.length_m.sum(), 1), "m")
for w in WINDOWS:
    m_all = (table[f"{w}_mean"] * table.length_m).sum() / table.length_m.sum()
    m_full = (full[f"{w}_mean"] * full.length_m).sum() / full.length_m.sum()
    print(f"{w:10s} length-weighted mean UTCI: all {m_all:.1f} | full only {m_full:.1f}"
          f" | highest p95 on route {table[f'{w}_p95'].max():.1f}")
print(table[["order", "segment_id", "name", "length_m", "coverage",
             "midday_mean", "midday_p95"]].round(1).to_string(index=False))
print("saved to", out)