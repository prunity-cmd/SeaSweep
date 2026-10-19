# Hermes sonar RTL: build, simulate, and compare against the Python model.
#   make        -> export vectors, simulate, compare (needs python3 + iverilog)
#   make clean

PY      ?= python3
IVERILOG?= iverilog
VVP     ?= vvp
SRC      = matched_filter.v envelope_decim.v tb_sonar_chain.v

all: compare

vectors/input.hex: ../sim/export_vectors.py ../sim/sonar_params.py
	$(PY) ../sim/export_vectors.py

sim.out: $(SRC) vectors/input.hex
	$(IVERILOG) -g2012 -o sim.out $(SRC)

run: sim.out
	$(VVP) sim.out

compare: run
	$(PY) ../sim/compare_rtl.py

clean:
	rm -rf sim.out vectors

.PHONY: all run compare clean
