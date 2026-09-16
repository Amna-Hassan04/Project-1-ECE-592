import csv
import os
import matplotlib.pyplot as plt

INPUT = "phase3/analysis/inclusion/hazel_inclusion_all.csv"
OUTDIR = "phase3/plots/inclusion"

os.makedirs(OUTDIR, exist_ok=True)

data = {}

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        machine = row["machine"]
        rounds = int(row["eviction_rounds"])
        median = float(row["median_timer_units"])

        data.setdefault(machine, []).append((rounds, median))

for machine in data:
    data[machine].sort()

    x = [p[0] for p in data[machine]]
    y = [p[1] for p in data[machine]]

    plt.figure(figsize=(7, 5))
    plt.plot(x, y, marker="o")
    plt.xlabel("Eviction rounds")
    plt.ylabel("Median timer units")
    plt.title(f"Hazel inclusion/exclusion timing: {machine}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    safe = machine.replace("/", "_")
    plt.savefig(os.path.join(OUTDIR, f"{safe}.png"), dpi=200)
    plt.savefig(os.path.join(OUTDIR, f"{safe}.pdf"))
    plt.close()

print(f"Created {len(data)} inclusion/exclusion plot pairs.")
