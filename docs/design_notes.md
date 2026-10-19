# Design notes

Working notes on key design choices. Numbers are targets or assumptions unless marked measured.

## Acoustic parameters

| Parameter | Value | Reason |
|---|---|---|
| Centre frequency | 455 kHz | Common side-scan frequency; transducers widely available; good balance of range (~30–50 m) and resolution for harbours |
| Chirp bandwidth | 100 kHz (405–505 kHz) | Range resolution c/2B = 0.75 cm (theoretical) |
| Chirp length | 64 µs (128 samples) | Time-bandwidth product 6.4; more energy on target without a high peak transmit voltage |
| Sample rate | 2 MS/s | Above 2 × highest frequency (505 kHz) for direct RF sampling |
| ADC | 12-bit signed | Enough dynamic range when combined with time-varying gain |
| Max range | 30 m per side (target) | Harbours and nearshore grounds |

## Signal chain

1. **TX:** MOSFET H-bridge drives the transducer with the chirp; T/R switch protects the receiver.
2. **AFE:** LNA → time-varying gain (compensates spreading loss) → anti-alias filter → ADC.
3. **FPGA:** matched filter (pulse compression) → |y| → peak-hold decimation by 8 → candidate detector.
4. **Pi:** waterfall assembly, int8 CNN classifier, geo-tagging, map.

## Why an FPGA

Pulse compression is a 128-tap FIR running at 2 MS/s per channel: about 512 million multiply-accumulates per second for two sides. That is heavy for a Pi CPU but cheap in FPGA DSP blocks, and the FPGA can run at a few hundred milliwatts. The Pi then sees data reduced 8× and only runs the classifier when needed.

## RTL plan

- **Now:** fully parallel transposed-form FIR, used as the bit-exact reference (`rtl/matched_filter.v`).
- **Next:** folded FIR sharing a few multipliers across taps, clocked at a multiple of the sample rate, to fit ECP5 DSP resources and cut power.
- **Later:** mix down to baseband I/Q and decimate before the matched filter, which cuts the multiply rate by roughly 10×.

## Power budget (assumed, to be measured)

| Block | Assumed draw |
|---|---|
| AFE + FPGA | 0.9 W |
| GPS, IMU, depth, MCU | 0.3 W |
| Raspberry Pi idle / active | 0.7 W / 2.4 W |
| Transmit | ~0.02 J per ping |

`firmware/duty_cycle_sim.py` estimates about 2.1 W average with adaptive duty cycling versus about 3.9 W always at high rate, under these assumptions.

## Known limitations

- Plastics and loose nets are weak acoustic targets; first classes are tyres, metal and bundled nets.
- The waterfall simulator is a toy model, not a physical sonar simulator.
- Classifier accuracy is unknown until we collect tank and field data.
