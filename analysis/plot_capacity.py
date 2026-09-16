import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "results", "capacity_summary.csv")
OUTDIR = os.path.join(ROOT, "results", "plots")

os.makedirs(OUTDIR, exist_ok=True)


# Read standardized summary
data = defaultdict(list)

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            machine = row["machine"]
            size_kib = float(row["working_set_kib"])
            median = float(row["median"])
            samples = int(row["samples"])
        except (KeyError, ValueError):
            continue

        data[machine].append((size_kib, median, samples))


# Remove duplicate measurements at the same size.
# Keep the measurement with the largest sample count.
clean = {}

for machine, rows in data.items():
    by_size = {}

    for size, median, samples in rows:
        if size not in by_size or samples > by_size[size][1]:
            by_size[size] = (median, samples)

    clean[machine] = sorted(
        (size, median, samples)
        for size, (median, samples) in by_size.items()
    )


# One plot per machine.
for machine, rows in sorted(clean.items()):

    x = [r[0] for r in rows]
    y = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.plot(x, y, marker="o", markersize=3, linewidth=1)

    ax.set_xscale("log", base=2)
    ax.set_xlabel("Working-set size (KiB)")
    ax.set_ylabel("Median timer units")
    ax.set_title(f"{machine.capitalize()} — Phase-I cache capacity sweep")

    ax.grid(True, which="both", alpha=0.25)

    fig.tight_layout()

    png = os.path.join(
        OUTDIR,
        f"{machine}_capacity_phase1.png"
    )

    pdf = os.path.join(
        OUTDIR,
        f"{machine}_capacity_phase1.pdf"
    )

    fig.savefig(png, dpi=300)
    fig.savefig(pdf)

    plt.close(fig)

    print(f"{machine}: {len(rows)} points")
    print(f"  {png}")
    print(f"  {pdf}")


# Combined chronological plot using normalized transition locations.
# This is intentionally NOT plotting timer values because timer units
# differ across architectures.
reference_capacity = {
    "sunbird": 32,
    "charnwood": 32,
    "ookay": 32,
    "upgrade": 32,
    "crux": 32,
    "skylark": 32,
    "thunderbird": 64,
    "artemisia": 48,
}

order = [
    "sunbird",
    "charnwood",
    "ookay",
    "upgrade",
    "crux",
    "skylark",
    "thunderbird",
    "artemisia",
]

fig, ax = plt.subplots(figsize=(8, 4.5))

for i, machine in enumerate(order):
    if machine not in reference_capacity:
        continue

    ax.scatter(
        reference_capacity[machine],
        i,
        s=55
    )

ax.set_yticks(range(len(order)))
ax.set_yticklabels([m.capitalize() for m in order])
ax.set_xlabel("Timing-inferred L1 capacity (KiB)")
ax.set_title("Phase-I timing-only cache-capacity inference")
ax.grid(True, axis="x", alpha=0.25)

fig.tight_layout()

png = os.path.join(OUTDIR, "phase1_l1_capacity_summary.png")
pdf = os.path.join(OUTDIR, "phase1_l1_capacity_summary.pdf")

fig.savefig(png, dpi=300)
fig.savefig(pdf)

plt.close(fig)

print()
print("Summary:")
print(png)
print(pdf)
