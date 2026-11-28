"""Heat layer: quick look at the SOLWEIG test numbers.
Run from the repo root:  python code/4_hazards/heat/4_check_test.py video5
"""
import sys

import numpy as np
import rasterio

sys.path.insert(0, "code")
import paths

label = sys.argv[1]
out = paths.where(label, "outputs") / "heat_test" / "output"
for kind in ("tmrt", "utci"):
    for f in sorted((out / kind).glob("*.tif")):
        with rasterio.open(f) as src:
            a = src.read(1)
        print(f"{f.name:28s} min {np.nanmin(a):5.1f}  mean {np.nanmean(a):5.1f}  max {np.nanmax(a):5.1f}")