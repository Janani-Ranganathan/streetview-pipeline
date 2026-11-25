import sys
import pandas as pd

label = sys.argv[1] if len(sys.argv) > 1 else "video"
g = pd.read_csv(f"data/gender_{label}.csv")

# One row for each group: walking, unsure, on_two_wheeler
rows = []
for move, grp in g.groupby("movement"):
    n = len(grp)
    w = (grp["gender_guess"] == "woman").sum()
    m = (grp["gender_guess"] == "man").sum()
    u = (grp["gender_guess"] == "uncertain").sum()
    rows.append({
        "video": label,
        "movement": move,
        "people": n,
        "women": w,
        "men": m,
        "uncertain": u,
        "share_women_low": round(w / n, 2),         # uncertain counted as men
        "share_women_high": round((w + u) / n, 2),  # uncertain counted as women
    })

out = pd.DataFrame(rows)
out.to_csv(f"data/summary_{label}.csv", index=False)
print(out.to_string(index=False))