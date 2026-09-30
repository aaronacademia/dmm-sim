# DMM Simulation & Automated Voltage Logger

Simulates a GPIB digital multimeter (DMM) using PyVISA and pyvisa-sim, then logs and plots DC voltage readings from a virtual 3V rail.

## What it does

- Loads a YAML instrument definition that responds to standard SCPI commands
- Queries `MEAS:VOLT:DC?` 30 times over a simulated GPIB connection
- Flags readings outside ±5% of 3V (2.85–3.15 V) as OUT OF RANGE
- Computes summary statistics (min, max, mean, std dev)
- Writes results to `readings.csv`
- Plots pass/fail readings to `voltage_plot.png`

## Why it matters

PyVISA is the standard Python library for controlling bench instruments (oscilloscopes, DMMs, power supplies) over GPIB, USB, and Ethernet. This project demonstrates automated test sequencing and data acquisition — the same workflow used in hardware validation and production test environments.

## Stack

- Python, PyVISA, pyvisa-sim, NumPy, Matplotlib

## Usage

```bash
python3 dmm_logger.py
```
