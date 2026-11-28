"""Heat layer: how much do tree pixels overlap building pixels?
Run from the repo root:  python code/4_hazards/heat/check_canopy_overlap.py
"""
import rasterio
from scipy.ndimage import distance_transform_edt

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"

with rasterio.open(FOLDER + r"\nanganallur_buildings_2023.tif") as src:
    presence = src.read(3)  # band 3 = building_presence
with rasterio.open(FOLDER + r"\nanganallur_canopy.tif") as src:
    canopy = src.read(1)

assert presence.shape == canopy.shape, "the two files are not on the same grid"

building = presence >= 0.5  # my choice of cut-off, we can change it
tree = canopy >= 3          # 3 m or taller counts as a tree

# for every building pixel: metres to the nearest non-building pixel (pixels are 1 m)
inside = distance_transform_edt(building)

print(f"building pixels: {building.mean():.1%} of the box")
print(f"tree pixels:     {tree.mean():.1%} of the box")
print(f"tree pixels that sit on a building pixel: {(tree & building).sum() / tree.sum():.1%}")
print(f"  (if trees ignored buildings, we would expect about {building.mean():.1%})")
for limit in (3, 6):
    deep = tree & (inside > limit)
    print(f"tree pixels more than {limit} m inside a building: {deep.sum() / tree.sum():.1%}")