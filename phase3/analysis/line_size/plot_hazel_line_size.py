import os
import csv
import matplotlib.pyplot as plt

ROOT = os.path.expanduser("~/Project-1-ECE-592")
INPUT = os.path.join(
    ROOT, "phase3", "analysis", "line_size",
    "hazel_line_size_all.csv"
)
OUTDIR = os.path.join(
    ROOT, "phase3", "plots", "line_size"
)

os.makedirs(OUTDIR, exist_ok=True)

rows = []

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            "machine": r["machine"],
            "offset": int(r["offset_bytes"]),
            "time": float(r["timer_units_per_access"])
        })

machines = sorted(set(r["machine"] for r in rows))

for machine in machines:
    data = [r for r in rows if r["machine"] == machine]
    data.sort(key=lambda r: r["offset"])

    x = [r["offset"] for r in data]
    y = [r["time"] for r in data]

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker="o")
    plt.axvline(64, linestyle="--", label="64 B reference")
    plt.xlabel("Access offset (bytes)")
    plt.ylabel("Median timer units per access")
    plt.title(f"Hazel line-size sweep: {machine}")
    plt.xticks(x, rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    safe_name = machine.replace("/", "_")

    png = os.path.join(
        OUTDIR, f"{safe_name}_line_size.png"
    )
    pdf = os.path.join(
        OUTDIR, f"{safe_name}_line_size.pdf"
    )

    plt.savefig(png, dpi=200)
    plt.savefig(pdf)
    plt.close()

print(f"Created {len(machines)} line-size plot pairs.")
print(f"Output directory: {OUTDIR}")
