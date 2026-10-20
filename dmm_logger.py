import csv
import time

import matplotlib
matplotlib.use("Agg")  # save to file without needing a display
import matplotlib.pyplot as plt
import numpy as np
import pyvisa

# Test settings
NOMINAL_V = 3.0
TOLERANCE = 0.05                       # ±5%
V_LOW = NOMINAL_V * (1 - TOLERANCE)    # 2.85 V
V_HIGH = NOMINAL_V * (1 + TOLERANCE)   # 3.15 V
NUM_SAMPLES = 30
SAMPLE_INTERVAL_S = 0.1

RESOURCE = "GPIB::1::INSTR"
SIM_CONFIG = "dmm.yaml@sim"
CSV_FILE = "readings.csv"
PLOT_FILE = "voltage_plot.png"


def in_range(v):
    return V_LOW <= v <= V_HIGH


# Point PyVISA at the simulation config
rm = pyvisa.ResourceManager(SIM_CONFIG)

# Open the virtual instrument
dmm = rm.open_resource(RESOURCE)
dmm.read_termination = "\n"
dmm.write_termination = "\n"

# Identify the instrument
idn = dmm.query("*IDN?")
print(f"Connected to: {idn.strip()}")

# Take NUM_SAMPLES readings, SAMPLE_INTERVAL_S apart
readings = []
print(f"Taking {NUM_SAMPLES} voltage readings...")
for i in range(NUM_SAMPLES):
    voltage = float(dmm.query("MEAS:VOLT:DC?"))
    readings.append(voltage)
    status = "OK" if in_range(voltage) else "OUT OF RANGE"
    print(f" [{i+1:02d}] {voltage:.4f} V {status}")
    time.sleep(SAMPLE_INTERVAL_S)

dmm.close()
rm.close()

# Summary stats
arr = np.array(readings)
results = ["OK" if in_range(v) else "OUT OF RANGE" for v in readings]
out_of_range = results.count("OUT OF RANGE")
print(f"\n--- Summary ---")
print(f"  Limits:        {V_LOW:.2f} to {V_HIGH:.2f} V ({NOMINAL_V} V ±{TOLERANCE:.0%})")
print(f"  Samples:       {NUM_SAMPLES}")
print(f"  Min:           {arr.min():.4f} V")
print(f"  Max:           {arr.max():.4f} V")
print(f"  Mean:          {arr.mean():.4f} V")
print(f"  Std dev:       {arr.std():.4f} V")
print(f"  Out of range:  {out_of_range}/{NUM_SAMPLES}")

# Write CSV
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["sample", "voltage_V", "result"])
    for i, (v, result) in enumerate(zip(readings, results)):
        writer.writerow([i + 1, round(v, 4), result])

print(f"Saved {CSV_FILE}")

# Plot
samples = range(1, NUM_SAMPLES + 1)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(samples, readings, color="#888888", linewidth=1, zorder=1)
ax.scatter(samples, readings,
           c=["#2ecc71" if r == "OK" else "#e74c3c" for r in results],
           s=50, zorder=2)
ax.axhline(V_LOW, color="#e67e22", linewidth=1.2, linestyle="--", label=f"Low limit ({V_LOW:.2f} V)")
ax.axhline(V_HIGH, color="#9b59b6", linewidth=1.2, linestyle="--", label=f"High limit ({V_HIGH:.2f} V)")
ax.set_xlabel("Sample")
ax.set_ylabel("Voltage (V)")
ax.set_title(f"DMM DC Voltage Readings: {NOMINAL_V:g} V Rail")
ax.legend()
plt.tight_layout()
plt.savefig(PLOT_FILE, dpi=150)

print(f"Saved {PLOT_FILE}")
