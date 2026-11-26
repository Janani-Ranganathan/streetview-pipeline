"""Finds the folder of a video from data/videos.csv.
Layout: <root>/<city>/<day_type>/<time_band>/<label>/
"""
import csv
from pathlib import Path


def row(label):
    with open("data/videos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["label"] == label:
                return r
    raise SystemExit(f"{label} is not in data/videos.csv. Add a row for it first.")


def where(label, root):
    r = row(label)
    p = Path(root) / r["city"] / r["day_type"] / r["time_band"] / label
    p.mkdir(parents=True, exist_ok=True)
    return p


def video_file(label):
    return row(label)["video_path"]
