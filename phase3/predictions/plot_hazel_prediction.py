import csv
import os
import matplotlib.pyplot as plt

csv_file = "data/hazel/capacity_summary.csv"
out_dir = "phase3/plots"
os.makedirs(out_dir, exist_ok=True)

sizes_kib = []
timings = []

with open(csv_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        sizes_kib.append(int(row["working_set_bytes"]) / 1024)
        timings.append(float(row["timer_units_per_access"]))

prediction_kib = 694.42

plt.figure(figsize=(9, 5.5))
plt.plot(sizes_kib, timings, marker="o", markersize=3, linewidth=1.2)
plt.axvline(
    prediction_kib,
    linestyle="--",
    linewidth=1.5,
    label=f"Frozen prediction: {prediction_kib:.2f} KiB"
)

plt.xscale("log", base=2)
plt.xlabel("Working-set size (KiB)")
plt.ylabel("Timer units per access")
plt.title("Hazel: Frozen L2 Capacity Prediction vs. Measured Timing")
plt.grid(True, which="both", alpha=0.25)
plt.legend()
plt.tight_layout()

plt.savefig(
    f"{out_dir}/hazel_frozen_prediction_vs_measured.png",
    dpi=300,
    bbox_inches="tight"
)
plt.savefig(
    f"{out_dir}/hazel_frozen_prediction_vs_measured.pdf",
    bbox_inches="tight"
)

print("Saved:")
print(f"  {out_dir}/hazel_frozen_prediction_vs_measured.png")
print(f"  {out_dir}/hazel_frozen_prediction_vs_measured.pdf")
