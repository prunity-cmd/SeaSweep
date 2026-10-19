# Hotspot mapping

`hotspot_map.py` converts geo-tagged detections into a hotspot map.

- **Input:** CSV with `lat, lon, label, confidence`
- **Output:** `hotspots.geojson` (25 m grid cells with score, detection count, dominant material, recyclable material) and `hotspots.png`

```bash
python hotspot_map.py --demo          # synthetic detections near Visakhapatnam
python hotspot_map.py detections.csv  # your own data
```

The GeoJSON opens in QGIS or geojson.io. Next: a simple offline dashboard (Telugu/English) for cooperatives and recyclers.
