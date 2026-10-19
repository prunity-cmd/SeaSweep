"""Check that the Verilog outputs match the Python reference bit for bit.

Run after `make` in rtl/ (the Makefile calls this automatically).
Saves rtl/vectors/rtl_vs_python.png.
"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sonar_params as P

V = Path(__file__).resolve().parent.parent / "rtl" / "vectors"


def load(name):
    return np.loadtxt(V / name, dtype=np.int64, ndmin=1)


ok = True
for ref_name, rtl_name, label in [("ref_mf.txt", "rtl_mf.txt", "matched filter"),
                                  ("ref_env.txt", "rtl_env.txt", "envelope")]:
    ref, rtl = load(ref_name), load(rtl_name)
    if len(ref) != len(rtl):
        print(f"FAIL {label}: length {len(rtl)} (RTL) vs {len(ref)} (Python)")
        ok = False
        continue
    mism = np.count_nonzero(ref != rtl)
    print(f"{'PASS' if mism == 0 else 'FAIL'} {label}: {len(ref)} samples, {mism} mismatches")
    ok &= mism == 0

env = load("rtl_env.txt")
r = (np.arange(len(env)) * P.DECIM - (P.N_TAPS - 1)) / P.FS * P.C_WATER / 2
plt.figure(figsize=(9, 3.5))
plt.plot(r, load("ref_env.txt"), lw=2.5, alpha=0.5, label="Python reference")
plt.plot(r, env, lw=0.8, label="Verilog (iverilog)")
plt.xlabel("range (m)")
plt.ylabel("envelope (counts)")
plt.title("RTL matched filter + envelope vs Python model")
plt.legend()
plt.tight_layout()
plt.savefig(V / "rtl_vs_python.png", dpi=150)
sys.exit(0 if ok else 1)
