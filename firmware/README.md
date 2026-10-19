# Firmware

`duty_cycle_sim.py` is a Python reference model of the adaptive duty-cycling controller that will run on the payload MCU. It switches between:

- **SCAN:** low ping rate, Raspberry Pi idle
- **INVESTIGATE:** high ping rate, Pi runs the classifier, triggered when the FPGA flags a candidate

and estimates average power and endurance. All power numbers are assumptions until bench measurement.

```bash
python duty_cycle_sim.py
```

Next: port the state machine to C on the MCU, and replace assumed power figures with measured ones.
