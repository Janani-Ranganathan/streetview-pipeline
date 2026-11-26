import sys
import pandas as pd

import sys as _s
from pathlib import Path as _P
_s.path.insert(0, str(_P(__file__).resolve().parents[1]))
from paths import where
label = sys.argv[1]
D = where(label, "data")
g = pd.read_csv(D / "gender.csv")

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
out.to_csv(D / "summary.csv", index=False)
print(out.to_string(index=False))