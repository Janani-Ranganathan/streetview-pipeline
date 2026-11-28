"""Heat layer, step 1: download hourly weather for one video.
Run from the repo root:  python code/4_hazards/heat/1_fetch_weather.py video5
Reads the video's date from data/videos.csv and saves the weather as a table.
"""
import sys

import pandas as pd
import requests

sys.path.insert(0, "code")  # lets this script import paths.py
import paths

LAT, LON = 12.98, 80.19  # middle of the Nanganallur route

label = sys.argv[1]  # the word typed after the script name, e.g. video5
video = paths.row(label)
date = video["date"]
if date == "":
    raise SystemExit(f"{label} has no date in data/videos.csv. Add it first.")

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": LAT,
    "longitude": LON,
    "start_date": date,
    "end_date": date,
    "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
              "shortwave_radiation,direct_radiation,diffuse_radiation",
    "wind_speed_unit": "ms",
    "timezone": "Asia/Kolkata",
}
answer = requests.get(url, params=params, timeout=60)
answer.raise_for_status()  # stops with a clear error if the website refuses
weather = pd.DataFrame(answer.json()["hourly"])

folder = paths.where(label, "outputs")
weather.to_csv(folder / "weather.csv", index=False)
print(f"Saved {len(weather)} hourly rows to {folder / 'weather.csv'}")

start = video["start_time"]
if start:
    hour = start[:2] + ":00"
    print(weather[weather["time"].str.endswith(hour)].to_string(index=False))