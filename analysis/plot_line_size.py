import csv
import glob
import os
import statistics

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results", "plots")
os.makedirs(OUT, exist_ok=True)


def read_raw(path):
    values = []

    with open(path) as f:
        for line in f:
            try:
                values.append(float(line.strip()))
            except ValueError:
                pass

    return values


# ------------------------------------------------------------
# Standard x86 measurements: 32B vs 64B
# ------------------------------------------------------------

standard = {
    "sunbird": ("line_dep_{}_final.txt"),
    "charnwood": ("line_{}_final.txt"),
    "crux": ("line_{}_final.txt"),
    "upgrade": ("line_{}_final.txt"),
    "ookay": ("line_{}_final.txt"),
    "artemisia": ("line_dep_{}_final.txt"),
}

for machine, pattern in standard.items():

    results = []

    for stride in [32, 64]:
        path = os.path.join(
            DATA,
            machine,
            pattern.format(stride)
        )

        if not os.path.isfile(path):
            continue

        values = read_raw(path)

        if not values:
            continue

        results.append((stride, statistics.median(values)))

    if not results:
        continue

    x = [r[0] for r in results]
    y = [r[1] for r in results]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    ax.plot(x, y, marker="o", linewidth=1.5)

    ax.set_xlabel("Access stride (bytes)")
    ax.set_ylabel("Median timer units")
    ax.set_title(f"{machine.capitalize()} — Line-size experiment")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, f"{machine}_line_size_phase1.png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, f"{machine}_line_size_phase1.pdf")
    )

    plt.close(fig)

    print(
        f"{machine}: "
        + ", ".join(f"{s}B={v:.2f}" for s, v in results)
    )


# ------------------------------------------------------------
# Skylark: detailed stride sweep
# ------------------------------------------------------------

path = os.path.join(DATA, "skylark", "line_size_stats.csv")

if os.path.isfile(path):

    results = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                filename = row["file"]
                stride = int(filename.split("_")[-1].split(".")[0])
                median = float(row["median_per_access"])
            except (KeyError, ValueError):
                continue

            results.append((stride, median))

    results.sort()

    if results:
        x = [r[0] for r in results]
        y = [r[1] for r in results]

        fig, ax = plt.subplots(figsize=(6.5, 4.5))

        ax.plot(x, y, marker="o", linewidth=1.5)

        ax.set_xlabel("Access stride (bytes)")
        ax.set_ylabel("Median timer units per access")
        ax.set_title("Skylark — Line-size experiment")
        ax.set_xticks(x)
        ax.grid(True, alpha=0.25)

        fig.tight_layout()

        fig.savefig(
            os.path.join(OUT, "skylark_line_size_phase1.png"),
            dpi=300
        )
        fig.savefig(
            os.path.join(OUT, "skylark_line_size_phase1.pdf")
        )

        plt.close(fig)

        print(
            "skylark: "
            + ", ".join(f"{s}B={v:.2f}" for s, v in results)
        )


# ------------------------------------------------------------
# Thunderbird: detailed stride sweep
# ------------------------------------------------------------

thunderbird = []

for stride in [32, 64, 128, 256]:

    path = os.path.join(
        DATA,
        "thunderbird",
        f"thunderbird_linesize_stride_{stride}.txt"
    )

    if not os.path.isfile(path):
        continue

    values = read_raw(path)

    if values:
        thunderbird.append(
            (stride, statistics.median(values))
        )

if thunderbird:

    x = [r[0] for r in thunderbird]
    y = [r[1] for r in thunderbird]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    ax.plot(x, y, marker="o", linewidth=1.5)

    ax.set_xlabel("Access stride (bytes)")
    ax.set_ylabel("Median timer units")
    ax.set_title("Thunderbird — Line-size experiment")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(OUT, "thunderbird_line_size_phase1.png"),
        dpi=300
    )
    fig.savefig(
        os.path.join(OUT, "thunderbird_line_size_phase1.pdf")
    )

    plt.close(fig)

    print(
        "thunderbird: "
        + ", ".join(f"{s}B={v:.2f}" for s, v in thunderbird)
    )


print()
print("LINE-SIZE PLOTS COMPLETE")
print(f"Output directory: {OUT}")
