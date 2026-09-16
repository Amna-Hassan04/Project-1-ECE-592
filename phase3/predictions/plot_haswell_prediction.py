import os
import re
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "phase3/data/hazel/Intel_R_Xeon_R_CPU_E5-2650_v3_2.30GHz"
PREDICTED_KIB = 694.42

OUTPUT_DIR = "phase3/plots"

PNG_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "haswell_frozen_prediction_vs_measured.png"
)

PDF_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "haswell_frozen_prediction_vs_measured.pdf"
)

rows = []

for filename in os.listdir(DATA_DIR):

    match = re.match(r"capacity_(\d+)\.txt$", filename)

    if match:
        size_bytes = int(match.group(1))
    else:
        match = re.match(r"capacity_dense_(\d+)\.txt$", filename)

        if not match:
            continue

        size_bytes = int(match.group(1))

    path = os.path.join(DATA_DIR, filename)

    with open(path, "r") as f:
        text = f.read()

    timer_match = re.search(
        r"Timer units/access:\s*([0-9.]+)",
        text
    )

    if timer_match is None:
        continue

    timer_per_access = float(timer_match.group(1))
    size_kib = size_bytes / 1024.0

    rows.append((size_kib, timer_per_access))

rows.sort(key=lambda item: item[0])

if not rows:
    raise RuntimeError(
        f"No capacity measurements found in {DATA_DIR}"
    )

x = np.array([row[0] for row in rows])
y = np.array([row[1] for row in rows])

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.figure(figsize=(9, 5.5))

# Actual Hazel measurement: SOLID line
plt.plot(
    x,
    y,
    marker="o",
    linestyle="-",
    linewidth=1.5,
    markersize=4,
    label="Hazel Haswell measured"
)

# Frozen ECE prediction: DOTTED line
plt.axvline(
    PREDICTED_KIB,
    linestyle=":",
    linewidth=2,
    label=f"Frozen ECE prediction = {PREDICTED_KIB:.2f} KiB"
)

plt.xlabel("Working-set size (KiB)")
plt.ylabel("Timer units per access")

plt.title(
    "Hazel Haswell Cache Capacity vs Frozen ECE Prediction"
)

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(PNG_OUTPUT, dpi=300)
plt.savefig(PDF_OUTPUT)

print("Hazel Haswell prediction plot created.")
print(f"Measurements plotted: {len(rows)}")
print(f"Frozen prediction: {PREDICTED_KIB:.2f} KiB")
print(f"PNG: {PNG_OUTPUT}")
print(f"PDF: {PDF_OUTPUT}")
