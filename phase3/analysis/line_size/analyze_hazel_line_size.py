import os
import glob
import re
import csv
import statistics

ROOT = os.path.expanduser("~/Project-1-ECE-592")
HAZEL = os.path.join(ROOT, "phase3", "data", "hazel")
OUTDIR = os.path.join(ROOT, "phase3", "analysis", "line_size")

os.makedirs(OUTDIR, exist_ok=True)


def read_value(path):
    values = []

    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Raw numeric line
            try:
                values.append(float(line))
                continue
            except ValueError:
                pass

            # line_size_bench output
            m = re.search(
                r"(?:Average|Median|Timer units/access|Elapsed.*?per.*?trial)"
                r".*?([0-9]+(?:\.[0-9]+)?)",
                line,
                re.IGNORECASE,
            )

            if m:
                try:
                    values.append(float(m.group(1)))
                except ValueError:
                    pass

    if not values:
        return None

    return statistics.median(values)


def offset_from_filename(path):
    name = os.path.basename(path)
    m = re.search(r"line_size_(\d+)\.txt$", name)

    if not m:
        return None

    return int(m.group(1))


def main():
    all_rows = []

    machines = sorted(
        d for d in os.listdir(HAZEL)
        if os.path.isdir(os.path.join(HAZEL, d))
    )

    for machine in machines:
        directory = os.path.join(HAZEL, machine)

        files = glob.glob(
            os.path.join(directory, "line_size_*.txt")
        )

        rows = []

        for path in files:
            offset = offset_from_filename(path)

            if offset is None:
                continue

            # Standard Hazel sweep ends at 224 B.
            if offset > 224:
                continue

            value = read_value(path)

            if value is None:
                continue

            rows.append({
                "machine": machine,
                "offset_bytes": offset,
                "timer_units_per_access": value,
                "file": os.path.relpath(path, ROOT),
            })

        rows.sort(key=lambda x: x["offset_bytes"])
        all_rows.extend(rows)

        print("=" * 80)
        print(machine)
        print("=" * 80)

        for row in rows:
            print(
                f"{row['offset_bytes']:4d} B  "
                f"median={row['timer_units_per_access']:12.4f}"
            )

        print(f"Points: {len(rows)}")
        print()

    output = os.path.join(
        OUTDIR,
        "hazel_line_size_all.csv"
    )

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "machine",
                "offset_bytes",
                "timer_units_per_access",
                "file",
            ],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print("=" * 80)
    print(f"Total measurements: {len(all_rows)}")
    print(f"Output: {output}")
    print("=" * 80)


if __name__ == "__main__":
    main()
