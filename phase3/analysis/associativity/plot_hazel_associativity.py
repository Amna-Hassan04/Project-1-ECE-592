import os
import csv
import matplotlib.pyplot as plt

ROOT = os.path.expanduser("~/Project-1-ECE-592")
INPUT = os.path.join(
    ROOT, "phase3", "analysis", "associativity",
    "hazel_associativity_all.csv"
)
OUTDIR = os.path.join(
    ROOT, "phase3", "plots", "associativity"
)

os.makedirs(OUTDIR, exist_ok=True)

rows = []

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            "machine": r["machine"],
            "assoc": int(r["conflicting_lines"]),
            "time": float(r["timer_units_per_access"])
        })

machines = sorted(set(r["machine"] for r in rows))

for machine in machines:
    data = sorted(
        [r for r in rows if r["machine"] == machine],
        key=lambda r: r["assoc"]
    )

    x = [r["assoc"] for r in data]
    y = [r["time"] for r in data]

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker="o")
    plt.xlabel("Number of conflicting cache lines")
    plt.ylabel("Timer units per access")
    plt.title(f"Hazel associativity sweep: {machine}")
    plt.xticks(x)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    safe = machine.replace("/", "_")

    plt.savefig(
        os.path.join(OUTDIR, f"{safe}_associativity.png"),
        dpi=200
    )
    plt.savefig(
        os.path.join(OUTDIR, f"{safe}_associativity.pdf")
    )
    plt.close()

print(f"Created {len(machines)} associativity plot pairs.")
print(f"Output directory: {OUTDIR}")
