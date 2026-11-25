import sys
from pathlib import Path
import cv2
import pandas as pd
from ultralytics import YOLO

# 1. Inputs: the video path, and a short label for the output files
video = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else "video"
Path(f"outputs/crops/{label}").mkdir(parents=True, exist_ok=True)

# 2. Pictures per second of the video
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()

# 3. Load the model. Classes: 0 = person, 1 = bicycle, 3 = motorcycle
model = YOLO("yolo11s.pt")
results = model.track(
    source=video,
    classes=[0, 1, 3],
    conf=0.3,
    persist=True,
    stream=True,
    verbose=False,
    save=True,
    project=str(Path("outputs").resolve()),
    name="tracked",
    exist_ok=True,
)

# 4. Go through the video picture by picture and save every box
rows = []
best_height = {}
for i, r in enumerate(results):
    n = len(r.boxes)
    if n == 0:
        continue
    seconds = i / fps
    boxes = r.boxes.xyxy.tolist()
    classes = r.boxes.cls.tolist()
    confs = r.boxes.conf.tolist()
    # a box with no ID number gets -1
    ids = r.boxes.id.tolist() if r.boxes.id is not None else [-1] * n
    for box, c, conf, pid in zip(boxes, classes, confs, ids):
        pid = int(pid)
        rows.append({
            "frame": i,
            "seconds": round(seconds, 3),
            "track_id": pid,
            "class": int(c),
            "conf": round(conf, 3),
            "x1": round(box[0]), "y1": round(box[1]),
            "x2": round(box[2]), "y2": round(box[3]),
        })
        # keep the biggest, clearest picture of each person
        if c == 0 and pid != -1:
            height = box[3] - box[1]
            if height >= best_height.get(pid, 0):
                best_height[pid] = height
                x1, y1 = max(0, int(box[0])), max(0, int(box[1]))
                crop = r.orig_img[y1:int(box[3]), x1:int(box[2])]
                if crop.size > 0:
                    cv2.imwrite(f"outputs/crops/{label}/{pid}.jpg", crop)

# 5. Save the big table of boxes
table = pd.DataFrame(rows)
table.to_csv(f"data/detections_{label}.csv", index=False)
print(len(table), "boxes saved")
print(table[table["class"] == 0]["track_id"].nunique(), "person tracks")