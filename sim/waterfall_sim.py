"""Synthetic side-scan 'waterfall' image built ping by ping.

Each ping: build a seabed reflectivity profile (water column, rough seabed,
debris objects with acoustic shadows), convolve with the chirp, add noise,
matched-filter, take the envelope, and stack pings along-track.

This is a toy model for visualisation and for early classifier experiments,
not a physically accurate sonar simulator.

Run:  python waterfall_sim.py     (saves waterfall.png)
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve, hilbert
import sonar_params as P

rng = np.random.default_rng(3)
MAX_RANGE = 30.0            # m
ALTITUDE = 4.0              # sonar height above seabed, m
N_PINGS = 300
ALONG_STEP = 0.1            # m travelled between pings
OUT_BINS = 600              # range bins in the output image

n = P.samples_for_range(MAX_RANGE)
r = np.arange(n) / P.FS * P.C_WATER / 2
dr = r[1] - r[0]
tx = P.chirp()
h = P.matched_filter_taps()

# Debris objects: (along-track m, slant range m, type)
OBJECTS = [(8.0, 10.0, "tyre"), (17.0, 18.0, "metal"), (24.0, 14.0, "net")]
NET_PTS = [(rng.normal(0, 1.0), rng.normal(0, 0.9)) for _ in range(400)]


def seabed():
    """Rough seabed: Rayleigh speckle, weaker at shallow grazing angles."""
    g = np.zeros_like(r)
    m = r > ALTITUDE
    graze = ALTITUDE / r[m]                       # sin(grazing angle)
    g[m] = graze ** 1.5 * rng.rayleigh(1.0, m.sum())
    return g


def shadow(prof, start_m, height_m):
    """Object of given height blocks returns behind it (flat-seabed geometry)."""
    length = start_m * height_m / max(ALTITUDE - height_m, 0.1)
    i0, i1 = np.searchsorted(r, [start_m, start_m + length])
    prof[i0:i1] *= 0.05


def add_objects(prof, y):
    for oy, orr, kind in OBJECTS:
        dy = y - oy
        if kind == "tyre" and abs(dy) < 0.7:      # ring: two bright edges
            hw = np.sqrt(0.7 ** 2 - dy ** 2)
            for edge in (orr - hw, orr + hw):
                i = np.searchsorted(r, edge)
                prof[i:i + 12] += 8.0
            shadow(prof, orr + hw + 0.05, 0.3)
        if kind == "metal" and abs(dy) < 1.0:     # strong compact reflector
            i = np.searchsorted(r, orr)
            prof[i:i + 60] += 12.0
            shadow(prof, orr + 60 * dr, 0.4)
        if kind == "net":                          # diffuse tangled texture
            for py, pr in NET_PTS:
                if abs(dy - py) < 0.1:
                    i = np.searchsorted(r, orr + pr)
                    prof[i:i + 6] += 4.0
    return prof


img = np.zeros((N_PINGS, OUT_BINS))
for p in range(N_PINGS):
    prof = add_objects(seabed(), p * ALONG_STEP)
    prof /= np.maximum(r, 1.0)                     # spreading loss
    echo = fftconvolve(prof, tx)[:n] + rng.normal(0, 0.01, n)
    mf = fftconvolve(echo, h)[P.N_TAPS - 1:P.N_TAPS - 1 + n]
    env = np.abs(hilbert(mf)) * np.maximum(r, 1.0) ** 1.6  # time-varying gain
    img[p] = env[: n - n % OUT_BINS].reshape(OUT_BINS, -1).max(axis=1)

db = 20 * np.log10(img / np.percentile(img, 99.5) + 1e-6)
plt.figure(figsize=(9, 6))
plt.imshow(db, cmap="copper", vmin=-30, vmax=3, aspect="auto",
           extent=[0, MAX_RANGE, N_PINGS * ALONG_STEP, 0])
for oy, orr, kind in OBJECTS:
    plt.annotate(kind, (orr, oy), xytext=(orr + 4, oy - 2), color="cyan", fontsize=9,
                 arrowprops=dict(arrowstyle="->", color="cyan", lw=0.8))
plt.xlabel("slant range (m)")
plt.ylabel("along-track distance (m)")
plt.title("Synthetic side-scan waterfall (one side): debris and acoustic shadows")
plt.colorbar(label="dB")
plt.tight_layout()
plt.savefig("waterfall.png", dpi=150)
print("Saved waterfall.png")
