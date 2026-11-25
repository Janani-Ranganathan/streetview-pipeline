import sys
import pandas as pd
from ultralytics import YOLO

# 1. Inputs: the video path and the same short label as before
video = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else "video"

# 2. Look for bicycles (1) and motorcycles (3) with a low bar of 0.1
model = YOLO("yolo11s.pt")
results = model.predict(
    source=video,
    classes=[1, 3],
    conf=0.1,
    stream=True,
    verbose=False,
)

# 3. Save every bike box with its picture number
rows = []
for i, r in enumerate(results):
    for box, c, conf in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist()):
        rows.append({
            "frame": i,
            "class": int(c),
            "conf": round(conf, 3),
            "x1": round(box[0]), "y1": round(box[1]),
            "x2": round(box[2]), "y2": round(box[3]),
        })

pd.DataFrame(rows).to_csv(f"data/bikes_{label}.csv", index=False)
print(len(rows), "bike boxes saved")