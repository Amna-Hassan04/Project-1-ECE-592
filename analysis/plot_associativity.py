import csv
import glob
import os
import re
import statistics

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results", "plots")
os.makedirs(OUT, exist_ok=True)


def raw_median(path):
    values = []

    with open(path) as f:
        for line in f:
            try:
                values.append(float(line.strip()))
            except ValueError:
                pass

    return statistics.median(values) if values else None


def artemisia_value(path):
    conflicting = None
    timer = None

    with open(path) as f:
        for line in f:
            if line.startswith("conflicting_lines="):
                conflicting = int(line.split("=", 1)[1])
            elif line.startswith("timer_units_per_access="):
                timer = float(line.split("=", 1)[1])

    return conflicting, timer


# ------------------------------------------------------------
# Standard x86 machines
# ------------------------------------------------------------

machines = {
    "charnwood": "assoc_{}_final.txt",
    "crux": "assoc_{}_final.txt",
    "upgrade": "assoc_{}_final.txt",
    "ookay": "assoc_{}_final.txt",
}

for machine, pattern in machines.items():

    results = []

    for ways in [8, 9, 10]:
        path = os.path.join(DATA, machine, pattern.format(ways))

        if not os.path.isfile(path):
            continue

        median = raw_median(path)

        if median is not None:
            results.append((ways, median))

    if not results:
        continue

    x = [r[0] for r in results]
    y = [r[1] for r in results]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    ax.plot(x, y, marker="o", linewidth=1.5)

    ax.set_xlabel("Conflicting lines")
    ax.set_ylabel("Median timer units")
    ax.set_title(f"{machine.capitalize()} — L1 associativity experiment")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, f"{machine}_associativity_phase1.png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, f"{machine}_associativity_phase1.pdf")
    )

    plt.close(fig)

    print(
        f"{machine}: "
        + ", ".join(f"{w}={v:.2f}" for w, v in results)
    )


# ------------------------------------------------------------
# Sunbird
# ------------------------------------------------------------

path = os.path.join(DATA, "sunbird", "associativity_l1_results.csv")

if os.path.isfile(path):

    results = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                ways = int(row["conflicting_lines"])
                value = float(row["timer_units_per_access"])
            except (KeyError, ValueError):
                continue

            results.append((ways, value))

    results.sort()

    if results:

        x = [r[0] for r in results]
        y = [r[1] for r in results]

        fig, ax = plt.subplots(figsize=(7, 4.5))

        ax.plot(x, y, marker="o", markersize=3, linewidth=1.2)

        ax.set_xlabel("Conflicting lines")
        ax.set_ylabel("Timer units per access")
        ax.set_title("Sunbird — L1 associativity experiment")
        ax.grid(True, alpha=0.25)

        fig.tight_layout()

        fig.savefig(
            os.path.join(OUT, "sunbird_associativity_phase1.png"),
            dpi=300
        )
        fig.savefig(
            os.path.join(OUT, "sunbird_associativity_phase1.pdf")
        )

        plt.close(fig)

        print(
            "sunbird: "
            + ", ".join(f"{w}={v:.2f}" for w, v in results)
        )


# ------------------------------------------------------------
# Skylark L1
# ------------------------------------------------------------

path = os.path.join(DATA, "skylark", "assoc_stats.csv")

if os.path.isfile(path):

    results = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                filename = row["file"]
                ways = int(
                    re.search(r"assoc_(\d+)\.txt", filename).group(1)
                )
                value = float(row["median_per_access"])
            except (KeyError, ValueError, AttributeError):
                continue

            results.append((ways, value))

    results.sort()

    if results:

        x = [r[0] for r in results]
        y = [r[1] for r in results]

        fig, ax = plt.subplots(figsize=(7, 4.5))

        ax.plot(x, y, marker="o", markersize=3, linewidth=1.2)

        ax.set_xlabel("Conflicting lines")
        ax.set_ylabel("Median timer units per access")
        ax.set_title("Skylark — L1 associativity experiment")
        ax.grid(True, alpha=0.25)

        fig.tight_layout()

        fig.savefig(
            os.path.join(OUT, "skylark_associativity_phase1.png"),
            dpi=300
        )
        fig.savefig(
            os.path.join(OUT, "skylark_associativity_phase1.pdf")
        )

        plt.close(fig)

        print(
            "skylark L1: "
            + ", ".join(f"{w}={v:.2f}" for w, v in results)
        )


# ------------------------------------------------------------
# Skylark L2
# ------------------------------------------------------------

path = os.path.join(DATA, "skylark", "assoc_l2_stats.csv")

if os.path.isfile(path):

    results = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                filename = row["file"]
                ways = int(
                    re.search(r"assoc_l2_(\d+)\.txt", filename).group(1)
                )
                value = float(row["median_per_access"])
            except (KeyError, ValueError, AttributeError):
                continue

            results.append((ways, value))

    results.sort()

    if results:

        x = [r[0] for r in results]
        y = [r[1] for r in results]

        fig, ax = plt.subplots(figsize=(7, 4.5))

        ax.plot(x, y, marker="o", markersize=3, linewidth=1.2)

        ax.set_xlabel("Conflicting lines")
        ax.set_ylabel("Median timer units per access")
        ax.set_title("Skylark — L2 associativity experiment")
        ax.grid(True, alpha=0.25)

        fig.tight_layout()

        fig.savefig(
            os.path.join(OUT, "skylark_l2_associativity_phase1.png"),
            dpi=300
        )
        fig.savefig(
            os.path.join(OUT, "skylark_l2_associativity_phase1.pdf")
        )

        plt.close(fig)

        print(
            "skylark L2: "
            + ", ".join(f"{w}={v:.2f}" for w, v in results)
        )


# ------------------------------------------------------------
# Artemisia
# ------------------------------------------------------------

paths = glob.glob(os.path.join(DATA, "artemisia", "assoc_l1*.txt"))

results = []

for path in paths:

    ways, value = artemisia_value(path)

    if ways is not None and value is not None:
        results.append((ways, value))

# Keep one value per conflicting-line count.
results = sorted(set(results))

if results:

    x = [r[0] for r in results]
    y = [r[1] for r in results]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.plot(x, y, marker="o", markersize=3, linewidth=1.2)

    ax.set_xlabel("Conflicting lines")
    ax.set_ylabel("Timer units per access")
    ax.set_title("Artemisia — L1 associativity experiment")
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, "artemisia_associativity_phase1.png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, "artemisia_associativity_phase1.pdf")
    )

    plt.close(fig)

    print(
        "artemisia: "
        + ", ".join(f"{w}={v:.2f}" for w, v in results)
    )


# ------------------------------------------------------------
# Thunderbird
# ------------------------------------------------------------

paths = glob.glob(
    os.path.join(DATA, "thunderbird", "thunderbird_assoc_*.txt")
)

results = []

for path in paths:

    match = re.search(r"thunderbird_assoc_(\d+)\.txt$", path)

    if not match:
        continue

    ways = int(match.group(1))
    median = raw_median(path)

    if median is not None:
        results.append((ways, median))

results.sort()

if results:

    x = [r[0] for r in results]
    y = [r[1] for r in results]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.plot(x, y, marker="o", markersize=3, linewidth=1.2)

    ax.set_xlabel("Conflicting lines")
    ax.set_ylabel("Median timer units")
    ax.set_title("Thunderbird — L1 associativity experiment")
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, "thunderbird_associativity_phase1.png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, "thunderbird_associativity_phase1.pdf")
    )

    plt.close(fig)

    print(
        "thunderbird: "
        + ", ".join(f"{w}={v:.2f}" for w, v in results)
    )


print()
print("ASSOCIATIVITY PLOTS COMPLETE")
print(f"Output directory: {OUT}")
