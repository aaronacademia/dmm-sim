import pyvisa
import time
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Point PyVISA at the simulation config
rm = pyvisa.ResourceManager("dmm.yaml@sim")

# Open the virtual intstrument
dmm = rm.open_resource("GPIB::1::INSTR")
dmm.read_termination = "\n"
dmm.write_termination = "\n"

# Identify the instrument
idn = dmm.query("*IDN?")
print(f"Connected to: {idn.strip()}")

# Take 30 readings, one per second
readings = []
print("Taking 30 voltage readings...")
for i in range(30):
    voltage = float(dmm.query("MEAS:VOLT:DC?"))
    readings.append(voltage)
    status = "OK" if 2.85 <= voltage <= 3.15 else "OUT OF RANGE"
    print(f" [{i+1:02d}] {voltage:.4f} V {status}")
    time.sleep(0.1)

dmm.close()
rm.close()

# Summary stats
arr = np.array(readings)
out_of_range = sum(1 for v in readings if not (2.85 <= v <= 3.15))
print(f"\n--- Summary ---")
print(f"  Samples:       30")
print(f"  Min:           {arr.min():.4f} V")
print(f"  Max:           {arr.max():.4f} V")
print(f"  Mean:          {arr.mean():.4f} V")
print(f"  Std dev:       {arr.std():.4f} V")
print(f"  Out of range:  {out_of_range}/30")

# Write CSV
with open("readings.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sample", "voltage_V", "result"])
    for i, v in enumerate(readings):
        result = "OK" if 2.85 <= v <= 3.15 else "OUT OF RANGE"
        writer.writerow([i+1, round(v, 4), result])

print("Saved readings.csv")

# Plot
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(range(1, 31), readings, color="#888888", linewidth=1, zorder=1)
ax.scatter(range(1, 31), readings,
           c=["#2ecc71" if 2.85 <= v <= 3.15 else "#e74c3c" for v in readings],
           s=50, zorder=2)
ax.axhline(2.85, color="#e67e22", linewidth=1.2, linestyle="--", label="Low limit (2.85 V)")
ax.axhline(3.15, color="#9b59b6", linewidth=1.2, linestyle="--", label="High limit (3.15 V)")
ax.set_xlabel("Sample")
ax.set_ylabel("Voltage (V)")
ax.set_title("DMM DC Voltage Readings — 3V Rail")
ax.legend()
plt.tight_layout()
plt.savefig("voltage_plot.png", dpi=150)

print("Saved voltage_plot.png")
