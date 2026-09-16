import csv
import os
import statistics

ROOT = "phase3/analysis"

# Timing-derived summary values
rows = [
    {
        "machine": "Intel Xeon E5-2650 v3",
        "generation": "Haswell",
        "vendor": "Intel",
        "capacity_inference": "~256 KiB L2; transition becomes pronounced above this region",
        "line_size": "64 B",
        "associativity": "~8-way effective L1 boundary",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "Intel Xeon E5-2650 v4",
        "generation": "Broadwell",
        "vendor": "Intel",
        "capacity_inference": "~256 KiB L2; gradual transition",
        "line_size": "64 B",
        "associativity": "~8-way effective L1 boundary",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "Intel Xeon Gold 6326",
        "generation": "Ice Lake",
        "vendor": "Intel",
        "capacity_inference": "Transition around ~1–2 MiB; timing-only exact capacity uncertain",
        "line_size": "Inconclusive",
        "associativity": "Inconclusive",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "Intel Xeon Platinum 8358",
        "generation": "Ice Lake",
        "vendor": "Intel",
        "capacity_inference": "Transition around ~1–2 MiB; timing-only exact capacity uncertain",
        "line_size": "Inconclusive",
        "associativity": "Inconclusive",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "Intel Xeon Platinum 8462Y+",
        "generation": "Sapphire Rapids",
        "vendor": "Intel",
        "capacity_inference": "Transition around ~1–2 MiB; timing-only exact capacity uncertain",
        "line_size": "Inconclusive",
        "associativity": "Inconclusive",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "AMD EPYC 9654",
        "generation": "Genoa",
        "vendor": "AMD",
        "capacity_inference": "Transition around ~512 KiB–1 MiB; timing-only exact capacity uncertain",
        "line_size": "64 B",
        "associativity": "~8-way effective boundary",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    },
    {
        "machine": "AMD EPYC 9655",
        "generation": "Genoa-or-newer",
        "vendor": "AMD",
        "capacity_inference": "Transition around ~512 KiB–1 MiB; timing-only exact capacity uncertain",
        "line_size": "64 B",
        "associativity": "Transition near 16 conflicting lines; exact associativity unresolved",
        "latency_note": "See latency sweep",
        "inclusion": "Inconclusive"
    }
]

out = os.path.join(ROOT, "summary", "hazel_timing_summary.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)

fields = [
    "machine",
    "generation",
    "vendor",
    "capacity_inference",
    "line_size",
    "associativity",
    "latency_note",
    "inclusion"
]

with open(out, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created: {out}")
print(f"Rows: {len(rows)}")
