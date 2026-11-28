"""Heat layer, step 3: first SOLWEIG test on a small piece of the box.
Run from the repo root:  python code/4_hazards/heat/3_solweig_test.py video5
"""
import sys
from datetime import datetime

import pandas as pd
import rasterio
import solweig
from rasterio.windows import Window

sys.path.insert(0, "code")
import paths

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
LAT, LON, UTC_OFFSET = 12.98, 80.19, 5.5
HOURS = [7, 8, 9, 10]  # test hours; each stamp is the END of the hour
WINDOW = Window(col_off=1382, row_off=1414, width=500, height=500)  # 500 m square, middle of the box

label = sys.argv[1]
out = paths.where(label, "outputs") / "heat_test"
out.mkdir(exist_ok=True)

# 1. cut a 500 m piece of buildings and trees and save it as small test files
with rasterio.open(FOLDER + r"\nanganallur_buildings_2023.tif") as src:
    height = src.read(2, window=WINDOW)
    presence = src.read(3, window=WINDOW)
    profile = src.profile
    transform = src.window_transform(WINDOW)
with rasterio.open(FOLDER + r"\nanganallur_canopy.tif") as src:
    canopy = src.read(1, window=WINDOW)

dsm = height * (presence >= 0.5)  # building height only where a building really is
profile.update(driver="GTiff", count=1, dtype="float32", height=500, width=500, transform=transform)
with rasterio.open(out / "test_dsm.tif", "w", **profile) as dst:
    dst.write(dsm.astype("float32"), 1)
with rasterio.open(out / "test_cdsm.tif", "w", **profile) as dst:
    dst.write(canopy.astype("float32"), 1)

# 2. prepare the surface (this also computes the sky view factor)
surface = solweig.SurfaceData.prepare(
    dsm=str(out / "test_dsm.tif"),
    cdsm=str(out / "test_cdsm.tif"),
    working_dir=str(out / "cache"),
)

# 3. weather for the test hours
table = pd.read_csv(paths.where(label, "outputs") / "weather.csv")
weather_list = []
for _, r in table.iterrows():
    t = datetime.fromisoformat(r["time"])
    if t.hour in HOURS:
        weather_list.append(solweig.Weather(
            datetime=t,
            ta=float(r["temperature_2m"]),
            rh=float(r["relative_humidity_2m"]),
            global_rad=float(r["shortwave_radiation"]),
            ws=float(r["wind_speed_10m"]),
        ))
print(f"{len(weather_list)} weather hours")

location = solweig.Location(latitude=LAT, longitude=LON, utc_offset=UTC_OFFSET)

# 4. run
summary = solweig.calculate(
    surface=surface,
    weather=weather_list,
    location=location,
    output_dir=str(out / "output"),
    outputs=["tmrt", "utci"],
    conifer=True,  # keep trees leafy in November
)

print("done. files:")
for f in sorted((out / "output").rglob("*.tif")):
    print(" ", f.relative_to(out))