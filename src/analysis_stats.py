import numpy as np
import csv
import glob
import os
import re

def analyze_file(filename):
    x = np.loadtxt(filename)

    return {
        "file": os.path.basename(filename),
        "n": len(x),
        "median_total": np.median(x),
        "mean_total": np.mean(x),
        "std_total": np.std(x, ddof=1),
        "q1_total": np.percentile(x, 25),
        "q3_total": np.percentile(x, 75),
        "p5_total": np.percentile(x, 5),
        "p95_total": np.percentile(x, 95),
        "min_total": np.min(x),
        "max_total": np.max(x),
        "median_per_access": np.median(x) / 1000.0,
        "mean_per_access": np.mean(x) / 1000.0
    }

def write_csv(files, output):
    rows = [analyze_file(f) for f in files]

    if not rows:
        return

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output} ({len(rows)} configurations)")

assoc_files = glob.glob("data/skylark/assoc_[0-9]*.txt")
assoc_files = [
    f for f in assoc_files
    if "_repeat" not in f
]

assoc_repeat_files = glob.glob("data/skylark/assoc_*_repeat.txt")

l2_files = glob.glob("data/skylark/assoc_l2_*.txt")

inclusion_files = glob.glob("data/skylark/inclusion_*.txt")

write_csv(
    sorted(assoc_files),
    "data/skylark/assoc_stats.csv"
)

write_csv(
    sorted(assoc_repeat_files),
    "data/skylark/assoc_repeat_stats.csv"
)

write_csv(
    sorted(l2_files),
    "data/skylark/assoc_l2_stats.csv"
)

write_csv(
    sorted(inclusion_files),
    "data/skylark/inclusion_stats.csv"
)

# Process 1M-sample latency/capacity experiments.
latency_files = glob.glob("data/skylark/latency_*.txt")

# Exclude the duplicate exploratory 32k file.
latency_files = [
    f for f in latency_files
    if not f.endswith("latency_32k.txt")
]

write_csv(
    sorted(latency_files),
    "data/skylark/latency_stats.csv"
)

# Process 1M-sample line-size experiments.
# Each sample times 2 dependent loads, so normalize by 2.
line_size_files = glob.glob("data/skylark/line_size_*.txt")

line_size_rows = []
for f in sorted(line_size_files):
    row = analyze_file(f)
    row["median_per_access"] = row["median_total"] / 2.0
    row["mean_per_access"] = row["mean_total"] / 2.0
    line_size_rows.append(row)

with open("data/skylark/line_size_stats.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=line_size_rows[0].keys())
    writer.writeheader()
    writer.writerows(line_size_rows)

print(f"Wrote data/skylark/line_size_stats.csv ({len(line_size_rows)} configurations)")
