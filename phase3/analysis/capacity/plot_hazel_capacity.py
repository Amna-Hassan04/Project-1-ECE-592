import os
import csv
import matplotlib.pyplot as plt

ROOT = os.path.expanduser("~/Project-1-ECE-592")
INPUT = os.path.join(
    ROOT, "phase3", "analysis", "capacity",
    "hazel_capacity_deduplicated.csv"
)
OUTPUT = os.path.join(ROOT, "phase3", "plots", "capacity")

os.makedirs(OUTPUT, exist_ok=True)

machines = {}

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        machine = row["machine"]

        machines.setdefault(machine, []).append({
            "size": float(row["working_set_bytes"]),
            "median": float(row["median_timer_units_per_access"]),
        })

for machine, rows in sorted(machines.items()):
    rows.sort(key=lambda x: x["size"])

    x = [r["size"] / 1024.0 for r in rows]
    y = [r["median"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, y, marker="o", linewidth=1.2, markersize=3)

    ax.set_xscale("log", base=2)

    ax.set_xlabel("Working-set size (KiB)")
    ax.set_ylabel("Timer units per access")
    ax.set_title(f"Hazel cache-capacity timing: {machine}")

    ax.grid(True, which="both", alpha=0.25)

    fig.tight_layout()

    safe_name = machine.replace("/", "_").replace(" ", "_")

    png = os.path.join(
        OUTPUT,
        safe_name + "_capacity.png"
    )
    pdf = os.path.join(
        OUTPUT,
        safe_name + "_capacity.pdf"
    )

    fig.savefig(png, dpi=200)
    fig.savefig(pdf)

    plt.close(fig)

    print(f"{machine}:")
    print(f"  points = {len(rows)}")
    print(f"  PNG = {png}")
    print(f"  PDF = {pdf}")

print()
print(f"Machines plotted: {len(machines)}")
