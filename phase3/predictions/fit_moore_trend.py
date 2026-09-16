import csv
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase3" / "data" / "ece_cache_history.csv"
OUT = ROOT / "phase3" / "predictions"

rows = []

with open(DATA, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = int(row["year"])
        capacity = float(row["l2_capacity_kib"])
        rows.append({
            "year": year,
            "capacity_kib": capacity,
            "log2_capacity": math.log2(capacity),
            "machine": row["machine"],
            "cpu": row["cpu"],
        })

x = np.array([r["year"] for r in rows], dtype=float)
y = np.array([r["log2_capacity"] for r in rows], dtype=float)

slope, intercept = np.polyfit(x, y, 1)

predicted = slope * x + intercept
ss_res = np.sum((y - predicted) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r2 = 1 - ss_res / ss_tot

doubling_years = 1.0 / slope

print("ECE Moore-style L2 trend")
print("========================")
print(f"Observations: {len(rows)}")
print(f"Slope (log2 KiB / year): {slope:.6f}")
print(f"Intercept: {intercept:.6f}")
print(f"R^2: {r2:.6f}")
print(f"Implied doubling interval: {doubling_years:.3f} years")
print()

print("Observations:")
for r in rows:
    print(
        f'{r["year"]}: {r["machine"]} '
        f'{r["capacity_kib"]:.0f} KiB '
        f'log2={r["log2_capacity"]:.3f}'
    )

# Save the fitted model parameters.
out = OUT / "moore_trend_model.txt"

with open(out, "w") as f:
    f.write("Frozen ECE Moore-style L2 trend model\n")
    f.write("=====================================\n")
    f.write(f"observations={len(rows)}\n")
    f.write(f"slope_log2_kib_per_year={slope:.12f}\n")
    f.write(f"intercept={intercept:.12f}\n")
    f.write(f"r_squared={r2:.12f}\n")
    f.write(f"implied_doubling_years={doubling_years:.12f}\n")

print()
print(f"Model saved to: {out}")
