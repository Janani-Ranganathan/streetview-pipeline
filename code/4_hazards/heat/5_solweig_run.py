"""Heat layer, step 5: SOLWEIG run for the whole box, for one video's day.
Run from the repo root:  python code/4_hazards/heat/5_solweig_run.py video5
"""
import sys
from datetime import datetime

import pandas as pd
import rasterio
import solweig

sys.path.insert(0, "code")
import paths

FOLDER = r"D:\THESIS\10. Web tool\5. Data\1. heat data"
LAT, LON, UTC_OFFSET = 12.98, 80.19, 5.5
HOURS = range(6, 20)  # 06:00 to 19:00; each stamp is the END of an hour

label = sys.argv[1]
out = paths.where(label, "outputs") / "heat_run"
out.mkdir(exist_ok=True)

# 1. surface files for the whole box
with rasterio.open(FOLDER + r"\nanganallur_buildings_2023.tif") as src:
    height = src.read(2)
    presence = src.read(3)
    crs, transform = src.crs, src.transform
with rasterio.open(FOLDER + r"\nanganallur_canopy.tif") as src:
    canopy = src.read(1)

dsm = height * (presence >= 0.5)  # building height only where a building really is


def save(name, array):
    with rasterio.open(out / name, "w", driver="GTiff", height=array.shape[0],
                       width=array.shape[1], count=1, dtype="float32",
                       crs=crs, transform=transform) as dst:
        dst.write(array.astype("float32"), 1)


save("dsm.tif", dsm)
save("cdsm.tif", canopy)

# 2. prepare the surface (walls and sky view factor, cached in the work folder)
surface = solweig.SurfaceData.prepare(
    dsm=str(out / "dsm.tif"),
    cdsm=str(out / "cdsm.tif"),
    working_dir=str(out / "cache"),
)

# 3. weather for the hours
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
solweig.calculate(
    surface=surface,
    weather=weather_list,
    location=location,
    output_dir=str(out / "output"),
    outputs=["tmrt", "utci"],
    conifer=True,  # keep trees leafy in November
)

n = len(list((out / "output" / "utci").glob("*.tif")))
print(f"done. {n} hourly UTCI maps in {out / 'output' / 'utci'}")