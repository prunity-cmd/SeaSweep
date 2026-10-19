# Hardware

Schematics and PCB layouts will be added here (KiCad). Current contents: `bom.csv`, with estimated prices from October 2026 that still need to be replaced with quotations.

## Planned boards

1. **AFE + TX board:** MOSFET H-bridge chirp driver, T/R switch, LNA, variable-gain amplifier for time-varying gain (candidate: AD8331), anti-alias filter, 12-bit ≥ 2 MS/s ADC (candidate: AD9226 module for the first prototype).
2. **Carrier:** FPGA board (ECP5 class) and Raspberry Pi, GPS/IMU/depth sensor headers, power management from a 12 V Li-ion pack.

## Housing

Acrylic or aluminium tube with O-ring end caps and rated cable penetrators. Target depth rating 30 m; pressure-test to 2× working depth before field use.

Hardware files will be released under CERN-OHL-P v2.
