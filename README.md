# streetview-pipeline

Part of the thesis **"A Spatial Analytical Framework for Climate Exposure and Women's Presence on Indian Streets"** (IAAC, MUPD 2026-27).
Status: work in progress. Last updated 25 Nov 2026.

## What this does

It turns a street video into a table: how many people are on the street, how many of them walk, how many ride a two-wheeler, and the share of visually inferred women. Results are reported only in aggregate.

The goal is one repeatable pipeline that works for any city. Later, the counts are joined to heat, flood and air layers by street piece and time of day.

## Pipeline (one video at a time)

| Step | Script | What it does |
|---|---|---|
| 1 | `code/track_people.py` | Detects and tracks people with YOLO11s. Saves every box in every picture, plus the best picture of each person (kept on the local machine only). |
| 2 | `code/find_bikes.py` | A second, more sensitive pass for bicycles and motorbikes (confidence 0.1). Bikes under riders are often missed at 0.3. |
| 3 | `code/analyse_tracks.py` | One row per person track. Removes non-people (the videographer's hand, number plates) and tiny far figures. Labels each person walking, on_two_wheeler or unsure, using overlap with bike boxes. |
| 4 | `code/guess_gender.py` | Zero-shot CLIP (ViT-L/14) on the best picture: woman or man, with an "uncertain" zone. |
| 5 | `code/summarise.py` | Counts per group and the women's share as a range. |
| 6 | `code/export_frames.py` | Saves annotated frames of the video (boxes coloured by woman, man or uncertain, labelled walk, ride or unsure) into `outputs/frames/`. Local only, because the pictures show real people. |

## How to run

```
pip install ultralytics transformers opencv-python pandas
python code/track_people.py "<path to video>" video5
python code/find_bikes.py "<path to video>" video5
python code/analyse_tracks.py video5
python code/guess_gender.py video5
python code/summarise.py video5
python code/export_frames.py "<path to video>" video5 0
```

Tested on Python 3.14, CPU only. The first run downloads model weights (YOLO11s about 18 MB, CLIP about 1.7 GB). Steps 1 and 2 take a few minutes per video. Steps 3 to 5 take seconds.

## First result: Chennai (Nanganallur), video 5, daytime, 2 min 20 s

| Group | People | Women | Men | Uncertain | Women's share |
|---|---|---|---|---|---|
| Walking | 17 | 8 | 7 | 2 | 47% to 59% |
| Unsure | 8 | 2 | 6 | 0 | 25% |
| On a two-wheeler | 11 | 1 | 8 | 2 | 9% to 27% |

The share is a range: the low end counts uncertain people as men, the high end counts them as women. 17 walkers are far too few for a finding. This row tests that the pipeline runs end to end.

## Rules used so far

- **Countable person:** best picture at least 100 px tall, taller than wide (aspect at least 1.2), seen in at least 5 pictures. This removes hands, plates and far figures.
- **Movement label:** share of a person's pictures where at least 30% of the person's box lies inside a bike box. At least 0.6 gives on_two_wheeler, 0.3 to 0.6 gives unsure, below 0.3 gives walking. The cut points were set by eye on this one video.
- **Gender guess:** probability of "woman" at least 0.65 gives woman, at most 0.35 gives man, anything between gives uncertain.

## Known limits

- The videos are 478 x 850 px and came through WhatsApp: no GPS, no recording time, compressed. Original files have been requested.
- The tracker loses people behind objects, so one person can become two tracks and counts run slightly high. Fast riders often get no track ID and drop out.
- The rider label is roughly 80% right in a visual check. It errs mostly on people standing beside parked scooters.
- The gender guess relies on clothing and view. It is weaker from behind and in dim light.
- Informal visual check of 32 review-sheet pictures: 26 agree, 4 uncertain, 2 wrong. These check labels are a draft and not yet independently verified. A proper labelled validation sample is planned.
- Only one daytime video has been run. The night video is untested.

## Data and privacy

Videos, pictures of people and model files are not in the repo. The tables hold one row per tracked person: box statistics and an inferred label. They hold no images and no names. Results are reported in aggregate only.

## Next steps

1. GPS traces from new rides, to place pictures on streets. Street pieces between junctions come from OpenStreetMap (OSMnx).
2. Time bins, then a join with heat (UTCI) by street piece and hour.
3. A labelled validation sample to report error rates.
4. Night video, then other cities.

## Questions for review

1. Is a three-way movement label, with the unsure group reviewed by eye, a sound approach?
2. What is the best way to validate visually inferred gender when only aggregates are reported?
3. Are there better tracker settings or models for a moving, handheld camera?
