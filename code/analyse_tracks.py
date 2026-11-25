import sys
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw

label = sys.argv[1] if len(sys.argv) > 1 else "video"

# 1. Read the two tables made by the slow scripts
det = pd.read_csv(f"data/detections_{label}.csv")
bikes = pd.read_csv(f"data/bikes_{label}.csv")

# 2. Keep only persons that have an ID number
people = det[(det["class"] == 0) & (det["track_id"] != -1)].copy()
bikes_by_frame = {f: g[["x1", "y1", "x2", "y2"]].values for f, g in bikes.groupby("frame")}

# 3. For one person box: how much of it sits inside the best-matching bike box (0 to 1)
def best_overlap(r):
    person_area = (r.x2 - r.x1) * (r.y2 - r.y1)
    best = 0
    for b in bikes_by_frame.get(r.frame, []):
        w = min(r.x2, b[2]) - max(r.x1, b[0])
        h = min(r.y2, b[3]) - max(r.y1, b[1])
        if w > 0 and h > 0 and person_area > 0:
            best = max(best, w * h / person_area)
    return best

people["bike_overlap"] = [best_overlap(r) for r in people.itertuples()]
people["height"] = people["y2"] - people["y1"]
people["width"] = people["x2"] - people["x1"]

# 4. One row per person track
rows = []
for pid, g in people.groupby("track_id"):
    best = g.loc[g["height"].idxmax()]          # the biggest, clearest picture
    rows.append({
        "track_id": pid,
        "first_s": round(g["seconds"].min(), 2),
        "last_s": round(g["seconds"].max(), 2),
        "pictures": len(g),
        "max_height_px": int(best["height"]),
        "aspect": round(best["height"] / best["width"], 2),   # tall person = big number
        "share_on_bike": round((g["bike_overlap"] >= 0.3).mean(), 2),
    })
table = pd.DataFrame(rows)

# 5. Countable = tall enough, taller than wide (not a hand), seen in 5+ pictures
table["countable"] = (
    (table["max_height_px"] >= 100) & (table["aspect"] >= 1.2) & (table["pictures"] >= 5)
)

# 6. Walking, on a two-wheeler, or unsure
table["movement"] = "walking"
table.loc[table["share_on_bike"] >= 0.3, "movement"] = "unsure"
table.loc[table["share_on_bike"] >= 0.6, "movement"] = "on_two_wheeler"
table.to_csv(f"data/people_{label}.csv", index=False)

ok = table[table["countable"]].sort_values("first_s")
print(len(table), "tracks,", len(ok), "countable")
print(ok["movement"].value_counts())

# 7. Review sheet: one picture per countable person, 25 per page
crops = Path(f"outputs/crops/{label}")
W, H = 200, 300
for page, start in enumerate(range(0, len(ok), 25), start=1):
    chunk = ok.iloc[start:start + 25]
    cols = 5
    rows_n = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows_n * (H + 22)), "white")
    draw = ImageDraw.Draw(sheet)
    for k, row in enumerate(chunk.itertuples()):
        x, y = (k % cols) * W, (k // cols) * (H + 22)
        p = crops / f"{row.track_id}.jpg"
        if p.exists():
            im = Image.open(p).convert("RGB")
            im.thumbnail((W - 4, H - 4))
            sheet.paste(im, (x + 2, y + 22))
        draw.text((x + 3, y + 5), f"id {row.track_id} {row.movement[:5]} {row.first_s:.0f}s", fill="black")
    sheet.save(f"outputs/review_{label}_{page}.jpg")
print("review sheets saved in outputs")