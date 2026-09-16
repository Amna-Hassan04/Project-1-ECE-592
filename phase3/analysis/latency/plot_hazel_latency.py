import csv
import os
import matplotlib.pyplot as plt

INPUT = "phase3/analysis/latency/hazel_latency_all.csv"
OUTDIR = "phase3/plots/latency"

os.makedirs(OUTDIR, exist_ok=True)

data = {}

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        machine = row["machine"]
        data.setdefault(machine, []).append(row)

for machine, rows in sorted(data.items()):
    rows.sort(key=lambda r: int(r["working_set_bytes"]))

    x = [float(r["working_set_kib"]) for r in rows]
    y = [float(r["timer_units_per_access"]) for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker="o")
    plt.xscale("log", base=2)

    plt.xlabel("Working-set size (KiB)")
    plt.ylabel("Timer units per dependent load")
    plt.title(f"Cache latency sweep — {machine}")
    plt.grid(True, which="both", alpha=0.3)

    plt.tight_layout()

    safe_name = machine.replace("/", "_")
    plt.savefig(
        os.path.join(OUTDIR, f"{safe_name}_latency.png"),
        dpi=200
    )
    plt.savefig(
        os.path.join(OUTDIR, f"{safe_name}_latency.pdf")
    )
    plt.close()

print(f"Created {len(data)} latency plot pairs.")
print(f"Output directory: {os.path.abspath(OUTDIR)}")
