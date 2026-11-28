# Heat layer: data sources (Nanganallur box)

Box (WGS84): west 80.175, south 12.965, east 80.205, north 12.995.
Output grid: UTM 44N (EPSG:32644), 1 m pixels, 3328 x 3264 pixels.
The data files live outside the repo in "5. Data/1. heat data".

## Buildings: nanganallur_buildings_2023.tif
- Source: Google Open Buildings 2.5D Temporal Dataset, snapshot 2023-06-30.
- Tiles: see docs/heat_tile_urls.txt (two tiles, joined along their shared edge).
- Bands: building_fractional_count, building_height, building_presence (float32).
- Native pixels are 0.5 m. Google states the effective detail is about 4 m.
  We read the window at 1 m with nearest-neighbour resampling.
- How it was made: the tile list came from Google's download notebook run in Colab
  (the notebook's own AI patched two lines for newer library versions).
  The cut-out was done with rasterio (merge with bounds and 1 m resolution).
- Heights are not validated for India by the data provider. Planned check:
  compare modelled shade with shade seen in the video frames.

## Trees: nanganallur_canopy.tif
- Source: Meta and WRI High Resolution Canopy Height Map v1, tile 123312212,
  s3://dataforgood-fb-data/forests/v1/alsgedi_global_v6_float/chm/123312212.tif
- Native: EPSG:3857, about 1.19 m pixels, uint8 (metres of height).
- Reprojected with nearest-neighbour onto the building grid above.
- Source imagery was taken at different dates, so this is not a 2023 snapshot.

## Checks done (28 Nov 2026)
- QGIS on the satellite map: building shapes line up with roofs, lanes show as gaps.
  Water bodies show no buildings. Trees: large green areas match, small speckles in
  dense blocks need ground truth from video frames.
- Overlap script (code/4_hazards/heat/check_canopy_overlap.py), cut-offs: building
  presence >= 0.5, tree >= 3 m. 18.6% of tree pixels sit on building pixels, against
  33.3% expected if trees ignored buildings. 4.2% are more than 3 m inside a building.

## Weather
- Open-Meteo Historical Weather API (ERA5 based), saved by 1_fetch_weather.py.
- To cite: Zippenfenig (2023) Open-Meteo.com Weather API; Hersbach et al. (2023) ERA5.