# Debris classifier

Status: planned. No real sonar data collected yet.

## Classes (first version)

See `classes.yaml`. We start with acoustically strong targets that sonar detects reliably: tyres, metal and bundled nets, plus seabed clutter as the negative class. Loose plastics are deliberately out of scope for version 1.

## Data plan

1. **Synthetic:** patches cut from `sim/waterfall_sim.py` output, to build and debug the pipeline only.
2. **Tank (CBIT, Dec 2026):** planted tyres, net bundles and metal pieces, recorded at several ranges and angles. Target ≥ 200 labelled patches.
3. **Lake and harbour (2027):** Hussain Sagar and Visakhapatnam, labelled against diver or camera ground truth.
4. **Public data:** forward-looking sonar marine debris datasets (see references) for pre-training, noting the sensor difference.

## Labelling format

One CSV row per patch: `patch_file, label, ping_index, range_bin, lat, lon, source (synthetic/tank/field), verified (yes/no)`.

## Model plan

Small CNN on 64 × 64 waterfall patches, quantised to int8 (TensorFlow Lite) to run on the Raspberry Pi. Every prediction carries a confidence score; low-confidence detections are flagged for diver or camera verification rather than reported as debris.

## Evaluation

Per-class precision and recall against ground truth, reported separately for synthetic, tank and field data.
