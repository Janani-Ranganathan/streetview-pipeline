import sys
import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, "code")
import paths

SEGMENTS = r"D:\THESIS\10. Web tool\5. Data\1. heat data\streets_nanganallur.gpkg"

label = sys.argv[1]
data = paths.where(label, "data")
out = paths.where(label, "outputs")

anchors = pd.read_csv(data / "anchors.csv").sort_values("time_s")
route = pd.read_csv(data / "route_segments.csv").sort_values("order")
people = pd.read_csv(data / "people.csv")
gender = pd.read_csv(data / "gender.csv")[["track_id", "p_woman", "gender_guess"]]

# length of each route segment, then distance where each one starts and ends
segs = gpd.read_file(SEGMENTS, layer="segments")
segs["length_m"] = segs.to_crs(32644).length
route = route.merge(segs[["segment_id", "length_m"]], on="segment_id")
route["end_m"] = route["length_m"].cumsum()
route["start_m"] = route["end_m"] - route["length_m"]
# length the clip really covers (the last segment is only partly filmed)
route["covered_m"] = (np.minimum(route.end_m, anchors.distance_m.max())
                      - np.maximum(route.start_m, anchors.distance_m.min())).clip(lower=0)

# middle time of each person -> distance along route -> segment
people["mid_s"] = (people.first_s + people.last_s) / 2
people["dist_m"] = np.interp(people.mid_s, anchors.time_s, anchors.distance_m)
idx = np.searchsorted(route.end_m.values, people.dist_m.values, side="left")
idx = idx.clip(0, len(route) - 1)
people["segment_id"] = route.segment_id.values[idx]
people = people.merge(gender, on="track_id", how="left")
people["woman"] = people.countable & (people.gender_guess == "woman")

people.to_csv(out / "encounters.csv", index=False)

summary = people.groupby("segment_id").agg(
    all_tracks=("track_id", "count"),
    countable=("countable", "sum"),
    women=("woman", "sum"),
)
summary = summary.reindex(route.segment_id).fillna(0)
summary["covered_m"] = route.set_index("segment_id")["covered_m"].round(0)
summary["countable_per_100m"] = (100 * summary.countable / summary.covered_m).round(1)
print(summary)
summary.to_csv(out / "encounters_by_segment.csv")
print("tracks seen outside the anchor times:",
      int(((people.mid_s < anchors.time_s.min()) | (people.mid_s > anchors.time_s.max())).sum()))