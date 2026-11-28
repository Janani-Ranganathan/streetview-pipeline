"""Heat layer, step 6: street segments (between intersections) for the box.
Run from the repo root:  python code/4_hazards/heat/6_streets.py
"""
import osmnx as ox

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
WEST, SOUTH, EAST, NORTH = 80.175, 12.965, 80.205, 12.995

# every street, lane and footpath in the box, from OpenStreetMap
graph = ox.graph_from_bbox(bbox=(WEST, SOUTH, EAST, NORTH), network_type="all")
graph = ox.convert.to_undirected(graph)  # one line per street piece, not one per direction
edges = ox.graph_to_gdfs(graph, nodes=False).reset_index()
edges = edges.to_crs(32644)  # UTM 44N, same as the heat maps

# list-valued columns (a street with two tags) become plain text
for col in ("highway", "name"):
    if col in edges.columns:
        edges[col] = edges[col].apply(lambda v: ", ".join(v) if isinstance(v, list) else v)

edges["segment_id"] = [f"nang_{i:04d}" for i in range(1, len(edges) + 1)]
edges["length_m"] = edges.geometry.length.round(1)
keep = edges[["segment_id", "name", "highway", "length_m", "geometry"]]
keep.to_file(FOLDER + r"\streets_nanganallur.gpkg", layer="segments", driver="GPKG")

print(f"{len(keep)} segments, {keep.length_m.sum() / 1000:.1f} km in total")
print(keep.length_m.describe().round(1))
print(keep.highway.value_counts().head(8))