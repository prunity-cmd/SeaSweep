"""Turn geo-tagged debris detections into a hotspot map.

Input CSV columns: lat, lon, label, confidence
  label in {tyre, net, metal, clutter}
Output:
  hotspots.geojson  grid cells with weighted debris score and dominant material
                    (opens in QGIS, geojson.io, or any web map)
  hotspots.png      quick-look heatmap

Run with synthetic demo data:   python hotspot_map.py --demo
Run with your own detections:   python hotspot_map.py detections.csv
"""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CELL_M = 25.0                          # grid cell size, metres
MIN_CONF = 0.5                         # ignore detections below this confidence
RECYCLABLE = {"tyre": "rubber", "net": "nylon net", "metal": "metal scrap"}


def demo_detections(path, n=400, seed=2):
    """Synthetic detections around an example harbour location."""
    rng = np.random.default_rng(seed)
    lat0, lon0 = 17.695, 83.295        # example coordinates near Visakhapatnam
    clusters = [(0.0010, 0.0005, "net"), (-0.0008, 0.0012, "tyre"), (0.0004, -0.0011, "metal")]
    rows = []
    for _ in range(n):
        if rng.random() < 0.75:
            dy, dx, lab = clusters[rng.integers(len(clusters))]
            lat = lat0 + dy + rng.normal(0, 0.00018)
            lon = lon0 + dx + rng.normal(0, 0.00018)
        else:
            lat = lat0 + rng.uniform(-0.002, 0.002)
            lon = lon0 + rng.uniform(-0.002, 0.002)
            lab = rng.choice(["clutter", "net", "tyre", "metal"], p=[0.7, 0.1, 0.1, 0.1])
        rows.append((lat, lon, lab, round(float(rng.uniform(0.4, 0.98)), 2)))
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lat", "lon", "label", "confidence"])
        w.writerows(rows)
    return path


def load(path):
    with open(path) as f:
        return [(float(r["lat"]), float(r["lon"]), r["label"], float(r["confidence"]))
                for r in csv.DictReader(f)]


def build_grid(dets):
    lat0 = np.mean([d[0] for d in dets])
    dlat = CELL_M / 111_320.0
    dlon = CELL_M / (111_320.0 * math.cos(math.radians(lat0)))
    cells = defaultdict(lambda: {"score": 0.0, "labels": Counter(), "count": 0})
    for lat, lon, lab, conf in dets:
        if conf < MIN_CONF or lab == "clutter":
            continue
        key = (math.floor(lat / dlat), math.floor(lon / dlon))
        cells[key]["score"] += conf
        cells[key]["labels"][lab] += conf
        cells[key]["count"] += 1
    return cells, dlat, dlon


def to_geojson(cells, dlat, dlon, path):
    feats = []
    for (i, j), c in cells.items():
        la, lo = i * dlat, j * dlon
        dom = c["labels"].most_common(1)[0][0]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [[
                [lo, la], [lo + dlon, la], [lo + dlon, la + dlat], [lo, la + dlat], [lo, la]]]},
            "properties": {"score": round(c["score"], 2), "detections": c["count"],
                           "dominant": dom, "recyclable_material": RECYCLABLE.get(dom, "unknown")},
        })
    feats.sort(key=lambda f: -f["properties"]["score"])
    with open(path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, indent=1)
    return feats


def plot(dets, feats, path):
    fig, ax = plt.subplots(figsize=(7, 6))
    scores = [f["properties"]["score"] for f in feats]
    vmax = max(scores) if scores else 1
    for f in feats:
        xs, ys = zip(*f["geometry"]["coordinates"][0])
        ax.fill(xs, ys, color=plt.cm.inferno(f["properties"]["score"] / vmax), alpha=0.85, lw=0)
    for f in feats[:5]:
        xs, ys = zip(*f["geometry"]["coordinates"][0])
        ax.text(np.mean(xs), np.mean(ys), f["properties"]["dominant"], fontsize=7,
                ha="center", color="cyan")
    ax.scatter([d[1] for d in dets], [d[0] for d in dets], s=2, c="grey", alpha=0.4)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title(f"Debris hotspots ({CELL_M:.0f} m cells, top 5 labelled)")
    ax.ticklabel_format(useOffset=False)
    plt.tight_layout()
    plt.savefig(path, dpi=150)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="?", help="detections CSV")
    ap.add_argument("--demo", action="store_true", help="generate synthetic detections")
    a = ap.parse_args()
    src = demo_detections("demo_detections.csv") if a.demo or not a.csv else a.csv
    dets = load(src)
    cells, dlat, dlon = build_grid(dets)
    feats = to_geojson(cells, dlat, dlon, "hotspots.geojson")
    plot(dets, feats, "hotspots.png")
    print(f"{len(dets)} detections -> {len(feats)} occupied cells")
    for f in feats[:5]:
        p = f["properties"]
        print(f"  score {p['score']:5.1f}  {p['detections']:3d} hits  {p['dominant']:6s} -> {p['recyclable_material']}")
    print("Saved hotspots.geojson and hotspots.png")
