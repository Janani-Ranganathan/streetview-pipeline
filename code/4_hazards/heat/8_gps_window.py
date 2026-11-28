"""Cut the GPS points of one video window out of a Google Timeline export."""
import csv
import json
from datetime import datetime
from pathlib import Path

FOLDER = Path(r"D:\THESIS\10. Web tool\2. Street view routes\Chennai - video 5")
# a little wider than the video (12:35 to 13:10 Chennai time) to catch the edges
START = datetime.fromisoformat("2026-11-22T00:00:00+05:30")
END = datetime.fromisoformat("2026-11-22T23:59:59+05:30")


def latlng(text):
    a, b = text.replace("°", "").split(",")
    return float(a), float(b)


d = json.load(open(FOLDER / "Timeline.json", encoding="utf-8"))
rows = []

for seg in d["semanticSegments"]:
    for p in seg.get("timelinePath", []):
        t = datetime.fromisoformat(p["time"])
        if START <= t <= END:
            lat, lon = latlng(p["point"])
            rows.append((t, lat, lon, "timelinePath", ""))

for r in d["rawSignals"]:
    pos = r.get("position")
    if not pos or "LatLng" not in pos:
        continue
    t = datetime.fromisoformat(pos["timestamp"])
    if START <= t <= END:
        lat, lon = latlng(pos["LatLng"])
        rows.append((t, lat, lon, "raw", pos.get("accuracyMeters", "")))

rows.sort(key=lambda x: x[0])
out = FOLDER / "track_video5.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["time", "lat", "lon", "kind", "accuracy_m"])
    for t, lat, lon, kind, acc in rows:
        w.writerow([t.astimezone(START.tzinfo).isoformat(), lat, lon, kind, acc])

print("points kept:", len(rows))
for kind in ("timelinePath", "raw"):
    k = [r for r in rows if r[3] == kind]
    if k:
        print(kind, len(k), k[0][0].astimezone(START.tzinfo).strftime("%H:%M:%S"),
              "to", k[-1][0].astimezone(START.tzinfo).strftime("%H:%M:%S"))
print("saved to", out)