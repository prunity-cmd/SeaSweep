"""Generate RTL test vectors and a bit-exact Python reference.

Writes to rtl/vectors/:
  coeffs.hex    quantised matched-filter taps (two's complement, 12-bit)
  input.hex     one simulated ping, quantised to 12-bit ADC samples
  tb_params.vh  `define NSAMP for the testbench
  ref_mf.txt    integer FIR output computed in Python
  ref_env.txt   integer envelope (|y| peak-hold, decimated) computed in Python

Run:  python export_vectors.py
"""
from pathlib import Path
import numpy as np
import sonar_params as P

OUT = Path(__file__).resolve().parent.parent / "rtl" / "vectors"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(11)

MAX_RANGE = 12.0                     # short ping keeps RTL simulation fast
TARGETS = [(3.0, 1.0), (6.5, 0.8), (10.0, 0.6)]


def to_hex(vals, bits):
    mask = (1 << bits) - 1
    return "\n".join(f"{int(v) & mask:0{(bits + 3) // 4}X}" for v in vals) + "\n"


# coefficients
h = P.quantize(P.matched_filter_taps(), P.COEF_BITS)

# one ping
n = P.samples_for_range(MAX_RANGE)
tx = P.chirp()
rx = np.zeros(n)
for r, a in TARGETS:
    i = P.samples_for_range(r)
    rx[i:i + len(tx)] += a / r * tx[: max(0, min(len(tx), n - i))]
rx += rng.normal(0, 0.03, n)
x = P.quantize(rx, P.ADC_BITS)

# bit-exact reference: y[n] = sum h[k] x[n-k], first n outputs
y = np.convolve(x, h)[:n].astype(np.int64)
assert np.max(np.abs(y)) < 2 ** (P.ACC_BITS - 1), "accumulator overflow"
nblk = n // P.DECIM
env = np.abs(y[: nblk * P.DECIM]).reshape(nblk, P.DECIM).max(axis=1)

(OUT / "coeffs.hex").write_text(to_hex(h, P.COEF_BITS))
(OUT / "input.hex").write_text(to_hex(x, P.ADC_BITS))
(OUT / "tb_params.vh").write_text(f"`define NSAMP {n}\n")
(OUT / "ref_mf.txt").write_text("\n".join(map(str, y)) + "\n")
(OUT / "ref_env.txt").write_text("\n".join(map(str, env)) + "\n")

bits_used = int(np.ceil(np.log2(np.max(np.abs(y)) + 1))) + 1
print(f"Wrote {n} samples, {len(h)} taps, {nblk} envelope outputs to {OUT}")
print(f"Peak FIR output uses {bits_used} of {P.ACC_BITS} accumulator bits")
