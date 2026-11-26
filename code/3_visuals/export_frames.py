"""Save annotated frames of one video into a folder (one picture every STEP seconds).
Run: python code/export_frames.py video5 1
The last number is the gap in seconds (1 = one picture per second, 0 = every frame).
"""
import sys
from pathlib import Path
import sys as _s
from pathlib import Path as _P
_s.path.insert(0, str(_P(__file__).resolve().parents[1]))
from paths import where, video_file
import cv2
import pandas as pd

label = sys.argv[1]
video = video_file(label)
step = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
D = where(label, "data")

det = pd.read_csv(D / "detections.csv")
gen = pd.read_csv(D / "gender.csv").set_index("track_id")
det = det[(det["class"] == 0) & (det.track_id.isin(gen.index))]
by_frame = {f: g for f, g in det.groupby("frame")}

# BGR colours: woman red, man blue, uncertain orange
COL = {"woman": (17, 42, 164), "man": (194, 181, 123), "uncertain": (31, 156, 237)}
TAG = {"woman": "W", "man": "M", "uncertain": "?"}
MOVE = {"walking": "walk", "on_two_wheeler": "ride", "unsure": "unsure"}

out = where(label, "outputs") / "frames"
out.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
every = 1 if step == 0 else max(1, round(step * fps))
n = saved = 0
while True:
    ok, img = cap.read()
    if not ok:
        break
    if n % every == 0:
        for r in by_frame.get(n, pd.DataFrame()).itertuples():
            g = gen.loc[r.track_id]
            c = COL[g.gender_guess]
            p1, p2 = (int(r.x1), int(r.y1)), (int(r.x2), int(r.y2))
            cv2.rectangle(img, p1, p2, c, 4)
            txt = f"{TAG[g.gender_guess]} {MOVE[g.movement]} #{r.track_id}"
            cv2.rectangle(img, (p1[0], max(0, p1[1] - 26)), (p1[0] + 12 * len(txt) + 8, max(26, p1[1])), c, -1)
            cv2.putText(img, txt, (p1[0] + 4, max(20, p1[1] - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"t = {n / fps:.1f} s", (10, img.shape[0] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(str(out / f"f_{n:05d}.jpg"), img)
        saved += 1
    n += 1
cap.release()
print(f"Done. {saved} pictures saved in {out.resolve()}")
