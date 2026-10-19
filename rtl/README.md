# RTL

| File | Purpose |
|---|---|
| `matched_filter.v` | 128-tap transposed-form FIR (pulse compression), 12-bit in, 32-bit out |
| `envelope_decim.v` | \|y\| followed by peak-hold decimation by D = 8 |
| `tb_sonar_chain.v` | Feeds a simulated ping through both blocks, dumps outputs |
| `Makefile` | Exports vectors from Python, runs Icarus Verilog, compares bit for bit |

```bash
make          # requires python3 (numpy, scipy, matplotlib) and iverilog
```

Expected output:

```
PASS matched filter: 32000 samples, 0 mismatches
PASS envelope: 4000 samples, 0 mismatches
```

## Next steps

- Synthesise for Lattice ECP5 with Yosys/nextpnr and record LUT, DSP and Fmax figures.
- Folded FIR (shared multipliers) to fit DSP resources and cut power.
- Baseband I/Q mixing and decimation before the matched filter.
- Candidate detector (threshold over local noise floor) that raises the wake signal for the Pi.
