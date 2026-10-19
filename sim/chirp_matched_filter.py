"""Single-ping simulation: chirp transmit, noisy echoes, matched filtering.

Shows why pulse compression matters: targets that are hard to see in the raw
noisy echo stand out clearly after the matched filter.

Run:  python chirp_matched_filter.py        (saves chirp_matched_filter.png)
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve, hilbert
import sonar_params as P

rng = np.random.default_rng(7)

MAX_RANGE = 30.0                       # metres
TARGETS = [                            # (range m, relative reflectivity, label)
    (8.0, 1.0, "tyre"),
    (17.5, 1.6, "metal scrap"),
    (24.0, 1.5, "net bundle"),
]
NOISE_STD = 0.05                       # noise level relative to transmit amplitude

n = P.samples_for_range(MAX_RANGE)
tx = P.chirp()
rx = np.zeros(n)
for r, a, _ in TARGETS:
    i = P.samples_for_range(r)
    rx[i:i + len(tx)] += a / r * tx[: max(0, min(len(tx), n - i))]   # 1/r spreading

rx_noisy = rx + rng.normal(0, NOISE_STD, n)

delay = P.N_TAPS - 1                   # matched-filter group delay
mf = fftconvolve(rx_noisy, P.matched_filter_taps())[delay:delay + n]
env = np.abs(hilbert(mf))
rng_axis = np.arange(n) / P.FS * P.C_WATER / 2

fig, ax = plt.subplots(3, 1, figsize=(10, 8))
ax[0].plot(np.arange(len(tx)) / P.FS * 1e6, tx)
ax[0].set_title(f"Transmit chirp: {P.F_CENTER/1e3:.0f} kHz centre, "
                f"{P.BANDWIDTH/1e3:.0f} kHz bandwidth, {P.T_CHIRP*1e6:.0f} us")
ax[0].set_xlabel("time (us)")
ax[1].plot(rng_axis, rx_noisy, lw=0.4)
ax[1].set_title("Raw received signal: weak echoes hard to see in noise")
ax[1].set_xlabel("range (m)")
env_db = 20 * np.log10(env / np.median(env) + 1e-9)
env_n = env / env.max()
ax[2].plot(rng_axis, env_n, lw=0.6)
for r, _, lab in TARGETS:
    ax[2].axvline(r, color="r", ls="--", lw=0.6, alpha=0.5)
    ax[2].text(r + 0.2, 0.9, lab, fontsize=8, color="r")
ax[2].set_title("After matched filter + envelope (normalised): targets stand out")
ax[2].set_xlabel("range (m)")
plt.tight_layout()
plt.savefig("chirp_matched_filter.png", dpi=150)

raw_db = 20 * np.log10(np.abs(hilbert(rx_noisy)) + 1e-12)
print(f"Theoretical range resolution: {P.range_resolution()*100:.2f} cm")
print(f"Time-bandwidth product:       {P.T_CHIRP*P.BANDWIDTH:.1f}")
for r, _, lab in TARGETS:
    i = P.samples_for_range(r)
    peak = env_db[max(0, i - 20): i + 20].max()
    print(f"  {lab:12s} at {r:5.1f} m -> {peak:5.1f} dB above noise after matched filter")
print("Saved chirp_matched_filter.png")
