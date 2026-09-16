import os
import csv
import statistics
from collections import defaultdict

ROOT = os.path.expanduser("~/Project-1-ECE-592")
INPUT = os.path.join(ROOT, "phase3", "analysis", "capacity",
                     "hazel_capacity_all.csv")
OUTPUT = os.path.join(ROOT, "phase3", "analysis", "capacity",
                      "hazel_capacity_deduplicated.csv")

groups = defaultdict(list)

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        key = (
            row["machine"],
            int(row["working_set_bytes"])
        )
        groups[key].append(float(row["median"]))

rows = []

for (machine, size), values in sorted(groups.items()):
    rows.append({
        "machine": machine,
        "working_set_bytes": size,
        "working_set_kib": size / 1024.0,
        "working_set_mib": size / (1024.0 * 1024.0),
        "observations": len(values),
        "median_timer_units_per_access": statistics.median(values),
        "mean_timer_units_per_access": statistics.mean(values),
        "min_timer_units_per_access": min(values),
        "max_timer_units_per_access": max(values),
    })

fields = [
    "machine",
    "working_set_bytes",
    "working_set_kib",
    "working_set_mib",
    "observations",
    "median_timer_units_per_access",
    "mean_timer_units_per_access",
    "min_timer_units_per_access",
    "max_timer_units_per_access",
]

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Input rows: {sum(len(v) for v in groups.values())}")
print(f"Unique machine/working-set points: {len(rows)}")
print(f"Output: {OUTPUT}")

duplicates = [
    (machine, size, len(values))
    for (machine, size), values in groups.items()
    if len(values) > 1
]

print()
print("Duplicated working-set points:")
for machine, size, count in duplicates:
    print(f"  {machine}: {size / 1024:.1f} KiB ({count} observations)")
