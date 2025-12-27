# Cocotb-Based-Functional-Verification-of-Data-Shifting-and-Pin-Mapping-Logic
This repository contains a cocotb-based verification environment developed to validate multi-lane data shifting and pin mapping logic. The testbench applies clock-driven stimulus, performs self-checking assertions, and measures functional coverage to ensure deterministic output behavior. Verification results are validated using waveform analysis and coverage closure.
### Repository Contents
- `dut.v` – RTL design under test  
- `test.py` – Cocotb-based self-checking testbench  
- `functional_coverage.yml` – Functional coverage report  
- `dut.vcd` – Waveform dump for signal-level analysis  

### Tools & Technologies
Verilog, Python, cocotb, cocotb-coverage, Icarus Verilog, GTKwaveform analysis
