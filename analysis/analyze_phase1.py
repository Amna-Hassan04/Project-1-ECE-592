import os
import glob
import re
import csv
import statistics

ROOT = os.path.expanduser("~/Project-1-ECE-592")
DATA = os.path.join(ROOT, "data")
RESULTS = os.path.join(ROOT, "results")

MACHINES = [
    "sunbird",
    "thunderbird",
    "skylark",
    "artemisia",
    "charnwood",
    "crux",
    "upgrade",
    "ookay",
]


def read_numeric_samples(path):
    values = []

    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Raw numeric sample format
            try:
                values.append(float(line))
                continue
            except ValueError:
                pass

            # Benchmark summary format:
            # Timer units/access: 32.3491
            m = re.search(r"Timer units/access:\s*([0-9.eE+-]+)", line)
            if m:
                try:
                    values.append(float(m.group(1)))
                except ValueError:
                    pass

    return values


def size_from_filename(filename):
    name = os.path.basename(filename).lower()

    # capacity_16k.txt, capacity_1024k.txt
    m = re.search(r"_(\d+)([km])(?:_final)?\.txt$", name)
    if m:
        value = int(m.group(1))
        unit = m.group(2)

        if unit == "k":
            return value * 1024

        if unit == "m":
            return value * 1024 * 1024

    # capacity_32768.txt
    # data_charnwood_32768.txt
    # dense_32768.txt
    m = re.search(r"_(\d+)(?:_final)?\.txt$", name)
    if m:
        return int(m.group(1))

    return None


def is_capacity_file(filename):
    name = os.path.basename(filename).lower()

    # Regular capacity sweeps
    if name.startswith("capacity_"):
        return True

    # Charnwood's original capacity naming
    if name.startswith("data_charnwood_"):
        return True

    # Dense capacity sweeps
    if name.startswith("dense_"):
        return True

    # Thunderbird dense capacity naming
    if name.startswith("thunderbird_capacity_dense_"):
        return True

    # Artemisia capacity/latency sweep uses latency_<bytes>.txt
    # as the raw timing measurement for each working-set size.
    if name.startswith("latency_"):
        return True

    return False


def summarize(values):
    return {
        "samples": len(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def analyze_machine(machine):
    directory = os.path.join(DATA, machine)
    rows = []

    if not os.path.isdir(directory):
        return rows

    # Standard raw timing files
    for path in sorted(glob.glob(os.path.join(directory, "*.txt"))):

        filename = os.path.basename(path)

        if not is_capacity_file(filename):
            continue

        size = size_from_filename(filename)

        if size is None:
            continue

        values = read_numeric_samples(path)

        if not values:
            continue

        stats = summarize(values)

        rows.append({
            "machine": machine,
            "file": os.path.relpath(path, ROOT),
            "working_set_bytes": size,
            "working_set_kib": size / 1024,
            "working_set_mib": size / (1024 * 1024),
            **stats,
        })

    # Sunbird dense capacity sweep is stored as a CSV:
    # working_set_bytes,timer_units_per_access
    sunbird_csv = os.path.join(directory, "capacity_dense_256k_512k.csv")

    if os.path.isfile(sunbird_csv):
        with open(sunbird_csv, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    size = int(row["working_set_bytes"])
                    value = float(row["timer_units_per_access"])
                except (KeyError, ValueError):
                    continue

                rows.append({
                    "machine": machine,
                    "file": os.path.relpath(sunbird_csv, ROOT),
                    "working_set_bytes": size,
                    "working_set_kib": size / 1024,
                    "working_set_mib": size / (1024 * 1024),
                    "samples": 1,
                    "median": value,
                    "mean": value,
                    "std": 0.0,
                    "min": value,
                    "max": value,
                })

    return rows

def main():

    all_rows = []

    for machine in MACHINES:

        rows = analyze_machine(machine)
        all_rows.extend(rows)

        print()
        print("=" * 80)
        print(machine.upper())
        print("=" * 80)

        if not rows:
            print("No capacity files parsed.")
            continue

        rows.sort(key=lambda x: x["working_set_bytes"])

        for r in rows:
            print(
                f"{r['working_set_kib']:10.1f} KiB  "
                f"median={r['median']:12.2f}  "
                f"mean={r['mean']:12.2f}  "
                f"samples={r['samples']:8d}  "
                f"{r['file']}"
            )

    output = os.path.join(RESULTS, "capacity_summary.csv")

    fields = [
        "machine",
        "file",
        "working_set_bytes",
        "working_set_kib",
        "working_set_mib",
        "samples",
        "median",
        "mean",
        "std",
        "min",
        "max",
    ]

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    print()
    print("=" * 80)
    print("CAPACITY ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Machines with data: {len(set(r['machine'] for r in all_rows))}")
    print(f"Total files:        {len(all_rows)}")
    print(f"Output:             {output}")


if __name__ == "__main__":
    main()
