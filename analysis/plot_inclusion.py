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


def median_raw(path):
    values = []

    with open(path) as f:
        for line in f:
            try:
                values.append(float(line.strip()))
            except ValueError:
                pass

    return statistics.median(values) if values else None


def make_plot(machine, x, y, xlabel, ylabel, title, filename):

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.plot(x, y, marker="o", markersize=4, linewidth=1.5)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, filename + ".png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, filename + ".pdf")
    )

    plt.close(fig)


# ------------------------------------------------------------
# Charnwood, Crux, Upgrade, Ookay
# ------------------------------------------------------------

standard = {
    "charnwood": "inclusion_{}.txt",
    "crux": "inclusion_{}_final.txt",
    "upgrade": "inclusion_{}_final.txt",
    "ookay": "inclusion_{}_final.txt",
}

for machine, pattern in standard.items():

    rows = []

    for size in [64, 128, 256, 512, 1024]:

        path = os.path.join(
            DATA,
            machine,
            pattern.format(size)
        )

        if not os.path.isfile(path):
            continue

        median = median_raw(path)

        if median is not None:
            rows.append((size, median))

    if not rows:
        continue

    rows.sort()

    x = [r[0] for r in rows]
    y = [r[1] for r in rows]

    make_plot(
        machine,
        x,
        y,
        "Eviction/test size (KiB)",
        "Median timer units",
        f"{machine.capitalize()} — Inclusion experiment",
        f"{machine}_inclusion_phase1"
    )

    print(
        f"{machine}: "
        + ", ".join(f"{s}={v:.2f}" for s, v in rows)
    )


# ------------------------------------------------------------
# Skylark
# ------------------------------------------------------------

path = os.path.join(DATA, "skylark", "inclusion_stats.csv")

if os.path.isfile(path):

    rows = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                filename = row["file"]
                size = int(
                    re.search(r"inclusion_(\d+)\.txt", filename).group(1)
                )
                value = float(row["median_per_access"])
            except (KeyError, ValueError, AttributeError):
                continue

            rows.append((size, value))

    rows.sort()

    if rows:

        x = [r[0] for r in rows]
        y = [r[1] for r in rows]

        make_plot(
            "skylark",
            x,
            y,
            "Experiment parameter",
            "Median timer units per access",
            "Skylark — Inclusion experiment",
            "skylark_inclusion_phase1"
        )

        print(
            "skylark: "
            + ", ".join(f"{s}={v:.3f}" for s, v in rows)
        )


# ------------------------------------------------------------
# Thunderbird
# ------------------------------------------------------------

paths = glob.glob(
    os.path.join(DATA, "thunderbird", "thunderbird_inclusion_*.txt")
)

for path in sorted(paths):

    values = []

    with open(path) as f:
        for line in f:
            try:
                values.append(float(line.strip()))
            except ValueError:
                pass

    if not values:
        continue

    median = statistics.median(values)

    print(
        "thunderbird:",
        os.path.basename(path),
        f"median={median:.2f}"
    )


print()
print("INCLUSION/EXCLUSION ANALYSIS COMPLETE")
print(f"Output directory: {OUT}")
