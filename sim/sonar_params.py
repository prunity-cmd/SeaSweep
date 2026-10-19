"""Shared signal parameters for the Hermes sonar simulations and RTL test vectors.

All values are design targets, not measured hardware values.
"""
import numpy as np

C_WATER = 1500.0          # speed of sound in water, m/s (nominal)
FS = 2_000_000            # ADC sample rate, Hz
F_CENTER = 455_000        # transducer centre frequency, Hz
BANDWIDTH = 100_000       # chirp bandwidth, Hz (405-505 kHz)
N_TAPS = 128              # chirp length in samples -> 64 us
T_CHIRP = N_TAPS / FS     # chirp duration, s

ADC_BITS = 12             # signed ADC samples
COEF_BITS = 12            # signed matched-filter coefficients
ACC_BITS = 32             # accumulator / FIR output width in RTL
DECIM = 8                 # envelope peak-hold decimation factor


def chirp(n=N_TAPS, fs=FS, fc=F_CENTER, bw=BANDWIDTH, window=True):
    """Real linear FM chirp centred on fc, with optional Hann taper."""
    t = np.arange(n) / fs
    f0 = fc - bw / 2
    k = bw / (n / fs)                      # sweep rate, Hz/s
    s = np.sin(2 * np.pi * (f0 * t + 0.5 * k * t ** 2))
    if window:
        s *= np.hanning(n)
    return s


def matched_filter_taps(n=N_TAPS):
    """Matched filter = time-reversed transmit chirp."""
    return chirp(n)[::-1]


def quantize(x, bits):
    """Scale to full range and round to signed integers of the given width."""
    full = 2 ** (bits - 1) - 1
    return np.round(x / np.max(np.abs(x)) * full).astype(np.int64)


def range_resolution():
    """Theoretical slant-range resolution c / 2B, in metres."""
    return C_WATER / (2 * BANDWIDTH)


def samples_for_range(r_m):
    """Two-way travel time to range r_m, in samples."""
    return int(round(2 * r_m / C_WATER * FS))
