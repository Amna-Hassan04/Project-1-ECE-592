import os
import glob
import re
import csv
import statistics

ROOT = os.path.expanduser("~/Project-1-ECE-592")
DATA = os.path.join(ROOT, "phase3", "data", "hazel")
OUTPUT = os.path.join(ROOT, "phase3", "analysis", "capacity")

os.makedirs(OUTPUT, exist_ok=True)


def read_numeric_samples(path):
    values = []

    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()

            try:
                values.append(float(line))
                continue
            except ValueError:
                pass

            m = re.search(r"Timer units/access:\s*([0-9.eE+-]+)", line)
            if m:
                values.append(float(m.group(1)))

    return values


def size_from_filename(filename):
    name = os.path.basename(filename)

    m = re.search(r"capacity(?:_dense)?_(\d+)\.txt$", name)
    if m:
        return int(m.group(1))

    return None


def summarize(values):
    return {
        "samples": len(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def analyze_machine(machine_dir):
    machine = os.path.basename(machine_dir)
    rows = []

    paths = sorted(glob.glob(os.path.join(machine_dir, "capacity*.txt")))

    for path in paths:
        filename = os.path.basename(path)
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
            "working_set_kib": size / 1024.0,
            "working_set_mib": size / (1024.0 * 1024.0),
            **stats,
        })

    rows.sort(key=lambda x: x["working_set_bytes"])
    return rows


def main():
    all_rows = []

    machine_dirs = [
        d for d in glob.glob(os.path.join(DATA, "*"))
        if os.path.isdir(d)
    ]

    for machine_dir in sorted(machine_dirs):
        rows = analyze_machine(machine_dir)

        if not rows:
            continue

        all_rows.extend(rows)

        machine = os.path.basename(machine_dir)

        output = os.path.join(
            OUTPUT,
            machine + "_capacity.csv"
        )

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
            writer.writerows(rows)

        print("=" * 80)
        print(machine)
        print("=" * 80)

        for row in rows:
            print(
                f"{row['working_set_kib']:10.1f} KiB  "
                f"median={row['median']:12.4f}  "
                f"samples={row['samples']:8d}"
            )

    combined = os.path.join(
        OUTPUT,
        "hazel_capacity_all.csv"
    )

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

    with open(combined, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    print()
    print(f"Total capacity measurements: {len(all_rows)}")
    print(f"Combined output: {combined}")


if __name__ == "__main__":
    main()
