"""Adaptive duty-cycling controller: reference model and power estimate.

This is the logic that will run on the payload MCU. It is written in Python
first so the state machine and power budget can be checked before porting to C.

States
  SCAN         clear seabed: low ping rate, Raspberry Pi idle
  INVESTIGATE  FPGA flagged a candidate: high ping rate, Pi runs the classifier
Returns to SCAN after CLEAR_PINGS consecutive pings with no candidate.

All power figures below are ASSUMPTIONS for planning, to be replaced with
bench measurements (see docs/design_notes.md).

Run:  python duty_cycle_sim.py
"""
import numpy as np

rng = np.random.default_rng(5)

# ---- assumed power draw, watts (replace with measured values) ----
P_AFE_FPGA = 0.9          # analog front end + FPGA, always on during survey
P_SENSORS = 0.3           # GPS, IMU, depth sensor, MCU
P_TX_PER_PING_J = 0.02    # energy per transmit pulse, joules
P_PI_IDLE = 0.7           # Raspberry Pi idle
P_PI_ACTIVE = 2.4         # Raspberry Pi running the classifier

# ---- controller parameters ----
PING_HZ_SCAN = 5.0
PING_HZ_INVESTIGATE = 15.0
CLEAR_PINGS = 30          # clear pings needed to drop back to SCAN

# ---- mission model ----
MISSION_S = 2 * 3600
DT = 0.1                  # simulation step, s
CANDIDATE_RATE_PER_MIN = 0.5   # how often the FPGA flags something (assumed)
CANDIDATE_LEN_S = 6.0          # how long an object stays in the swath
BATTERY_WH = 12 * 10           # 12 V, 10 Ah pack


def simulate(adaptive=True):
    state, clear, energy, t_inv = "SCAN", 0, 0.0, 0.0
    t_obj_end = -1.0
    ping_acc = 0.0
    for step in range(int(MISSION_S / DT)):
        t = step * DT
        if rng.random() < CANDIDATE_RATE_PER_MIN / 60 * DT:
            t_obj_end = t + CANDIDATE_LEN_S
        candidate = t < t_obj_end

        if not adaptive:
            state = "INVESTIGATE"
        elif state == "SCAN" and candidate:
            state, clear = "INVESTIGATE", 0
        elif state == "INVESTIGATE":
            ping_hz = PING_HZ_INVESTIGATE
            clear = 0 if candidate else clear + ping_hz * DT
            if clear >= CLEAR_PINGS:
                state = "SCAN"

        ping_hz = PING_HZ_INVESTIGATE if state == "INVESTIGATE" else PING_HZ_SCAN
        pi_w = P_PI_ACTIVE if state == "INVESTIGATE" else P_PI_IDLE
        ping_acc += ping_hz * DT
        energy += (P_AFE_FPGA + P_SENSORS + pi_w) * DT
        t_inv += DT if state == "INVESTIGATE" else 0.0
    energy += ping_acc * P_TX_PER_PING_J
    return energy / MISSION_S, t_inv / MISSION_S


for name, adaptive in [("Always high-rate (baseline)", False), ("Adaptive duty cycling", True)]:
    avg_w, frac = simulate(adaptive)
    print(f"{name:30s} avg {avg_w:4.2f} W | investigate {frac*100:5.1f}% of time | "
          f"est. endurance {BATTERY_WH/avg_w:4.1f} h on {BATTERY_WH} Wh")
print("\nAll figures use assumed power numbers; update after bench measurement.")
