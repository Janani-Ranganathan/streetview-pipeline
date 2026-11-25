import sys
import pandas as pd
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

label = sys.argv[1] if len(sys.argv) > 1 else "video"

# 1. Only the countable people from the analysis table
people = pd.read_csv(f"data/people_{label}.csv")
people = people[people["countable"]].copy()

# 2. Load CLIP: a model that matches pictures to sentences
name = "openai/clip-vit-large-patch14"
model = CLIPModel.from_pretrained(name)
processor = CLIPProcessor.from_pretrained(name)
model.eval()

# 3. Two sentences per group, so one odd sentence cannot decide alone
texts = [
    "a photo of a woman",
    "a full-body photo of a woman on a street",
    "a photo of a man",
    "a full-body photo of a man on a street",
]

# 4. For each person's best picture: how likely is "woman" against "man"?
p_woman = []
for pid in people["track_id"]:
    path = f"outputs/crops/{label}/{pid}.jpg"
    im = Image.open(path).convert("RGB")
    inputs = processor(text=texts, images=im, return_tensors="pt", padding=True)
    with torch.no_grad():
        out = model(**inputs)
    l = out.logits_per_image[0]
    w = (l[0] + l[1]) / 2
    m = (l[2] + l[3]) / 2
    p_woman.append(torch.softmax(torch.stack([w, m]), dim=0)[0].item())

people["p_woman"] = [round(p, 2) for p in p_woman]

# 5. Turn the chance into a guess, with a middle zone for "uncertain"
people["gender_guess"] = "uncertain"
people.loc[people["p_woman"] >= 0.65, "gender_guess"] = "woman"
people.loc[people["p_woman"] <= 0.35, "gender_guess"] = "man"

people.to_csv(f"data/gender_{label}.csv", index=False)
print(pd.crosstab(people["movement"], people["gender_guess"]))