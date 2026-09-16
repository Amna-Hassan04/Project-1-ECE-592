import glob
import os
import re
import statistics

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results", "plots")
os.makedirs(OUT, exist_ok=True)


def median_raw(path):
    values = []

    with open(path) as f:
        for line in f:
            try:
                values.append(float(line.strip()))
            except ValueError:
                pass

    return statistics.median(values) if values else None


def size_from_name(path):
    name = os.path.basename(path).lower()

    m = re.search(r"_(\d+)([km])(?:_final)?\.txt$", name)
    if m:
        value = int(m.group(1))
        return value * (1024 if m.group(2) == "k" else 1024 * 1024)

    m = re.search(r"_(\d+)(?:_final)?\.txt$", name)
    if m:
        return int(m.group(1))

    return None


def collect(machine, pattern):
    rows = []

    for path in glob.glob(os.path.join(DATA, machine, pattern)):
        size = size_from_name(path)

        if size is None:
            continue

        median = median_raw(path)

        if median is not None:
            rows.append((size, median))

    return sorted(rows)


machines = {
    "sunbird": ["latency_*_final.txt"],
    "skylark": ["latency_*.txt"],
    "artemisia": ["latency_*.txt"],
    "thunderbird": ["thunderbird_latency_*.txt"],
}


for machine, patterns in machines.items():

    rows = []

    for pattern in patterns:
        rows.extend(collect(machine, pattern))

    # Remove duplicate working-set sizes, keeping the first occurrence.
    unique = {}
    for size, median in rows:
        if size not in unique:
            unique[size] = median

    rows = sorted(unique.items())

    if not rows:
        print(f"{machine}: no latency data")
        continue

    sizes_kib = [size / 1024 for size, _ in rows]
    medians = [median for _, median in rows]

    plt.figure(figsize=(10, 6))
    plt.plot(
        sizes_kib,
        medians,
        marker="o",
        linewidth=2
    )

    plt.xscale("log", base=2)

    plt.xlabel("Working-set size (KiB)")
    plt.ylabel("Median timer units per access")
    plt.title(f"{machine.capitalize()} — Cache latency experiment")
    plt.grid(True, alpha=0.25)

    plt.tight_layout()

    png = os.path.join(OUT, f"{machine}_latency.png")
    pdf = os.path.join(OUT, f"{machine}_latency.pdf")

    plt.savefig(png, dpi=200)
    plt.savefig(pdf)
    plt.close()

    print(
        f"{machine}: {len(rows)} points, "
        f"{sizes_kib[0]:.0f} KiB–{sizes_kib[-1]:.0f} KiB"
    )

print("\nLATENCY PLOTS COMPLETE")
print(f"Output directory: {OUT}")
