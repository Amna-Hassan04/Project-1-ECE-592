# Predicting Cache Evolution: The Growing Capacity and Latency Cost of CPU Caching

This repository contains the code, experimental data, analysis scripts, plots, and report for **ECE 592: Reverse Engineering Microarchitecture** at North Carolina State University.

The project investigates CPU cache organization using timing-based microbenchmarks and hardware performance monitoring counters (PMUs). The work first reverse engineers cache properties on eight heterogeneous systems available in Prof. Samira Mirbagher Ajorpaz's lab and then evaluates the methodology on heterogeneous systems from the **NC State ECE Department Hazel HPC cluster**.

## Project Overview

The project is organized into three main phases:

### Phase I — Timing-Based Cache Reverse Engineering

Cache properties are inferred using controlled memory-access experiments without relying on published specifications as the primary measurement source.

The experiments investigate:

- Cache capacity
- Cache-line size
- Cache associativity
- Cache hit latency
- Miss and next-level latency
- Cache inclusion/exclusion behavior

The main benchmark uses randomized dependent pointer chasing to reduce memory-level parallelism and make cache-level transitions visible through timing measurements.

### Phase II — Performance Monitoring Counter Validation

Hardware performance monitoring counters (PMUs) are used as an independent source of evidence for the timing-based observations.

Because PMU events differ across processor architectures, the experiments use the cache-related events available on each system and document architecture-specific event mappings and limitations.

The Phase-II results are compared with the timing-based cache-capacity and associativity observations from Phase I.

### Phase III — Cross-Generation Validation and Prediction

The timing methodology is applied to heterogeneous systems available through the NC State ECE Hazel HPC environment.

The project then studies cache capacity across the processor generations measured in the laboratory data and constructs a frozen empirical prediction for an unseen generation.

Two empirical cache laws are also formulated from the ECE laboratory measurements:

1. **Hassan L2 Capacity Scaling Law**
2. **Hassan Cache-Line Stability Law**

The predictions are evaluated against held-out Hazel measurements without refitting the original models.

## Systems

### ECE Laboratory Systems

Phase-I and Phase-II experiments were performed on eight servers available in **Prof. Samira Mirbagher Ajorpaz's lab**, covering Intel, AMD, and Arm processors.

| Machine | Processor / Generation |
|---|---|
| Sunbird | Intel Xeon E5-2680 v3 / Haswell |
| Charnwood | Intel Core i7-6700 / Skylake |
| Ookay | Intel Core i7-7700 / Kaby Lake |
| Upgrade | Intel Core i7-8700 / Coffee Lake |
| Crux | Intel Core i7-9700 / Coffee Lake |
| Skylark | AMD EPYC 7532 / Zen 2 |
| Thunderbird | Ampere Altra Q80-30 / Neoverse-N1 |
| Artemisia | Intel Xeon Gold 5420+ / Sapphire Rapids |

### Hazel Systems

Phase-III validation was performed on heterogeneous **NC State ECE Department Hazel HPC servers**.

The retained measurements include:

- Intel Xeon E5-2650 v3 — Haswell
- Intel Xeon E5-2650 v4 — Broadwell
- Intel Xeon Gold 6326 — Ice Lake
- Intel Xeon Platinum 8358 — Ice Lake
- Intel Xeon Platinum 8462Y+ — Sapphire Rapids
- AMD EPYC 9654 — Genoa
- AMD EPYC 9655 — Genoa-or-newer

## Repository Structure

```text
Project-1-ECE-592/
├── src/                         # Core reverse-engineering benchmarks
│   ├── common/                 # Shared pointer-chasing and timing interfaces
│   ├── x86_64/                 # x86-64 timing implementation
│   └── aarch64/                # AArch64 timing implementation
│
├── experiments/                # Experiment launch scripts
│   └── capacity/
│       └── run_sweep.sh
│
├── data/                       # Raw Phase-I and Phase-II measurements
│   ├── sunbird/
│   ├── charnwood/
│   ├── skylark/
│   ├── artemisia/
│   ├── crux/
│   ├── upgrade/
│   ├── ookay/
│   └── thunderbird/
│
├── analysis/                   # Phase-I analysis and visualization
│   ├── analyze_phase1.py
│   ├── plot_capacity.py
│   ├── plot_associativity.py
│   ├── plot_line_size.py
│   ├── plot_latency.py
│   └── plot_inclusion.py
│
├── phase3/                     # Cross-generation and Hazel validation
│   ├── data/                   # ECE chronology + Hazel measurements
│   ├── analysis/               # Hazel result analysis
│   │   ├── capacity/
│   │   ├── latency/
│   │   ├── associativity/
│   │   ├── line_size/
│   │   └── inclusion/
│   │
│   ├── predictions/            # Frozen predictions and cache-evolution models
│   │   ├── fit_moore_trend.py
│   │   ├── moore_trend_model.txt
│   │   ├── frozen_hazel_prediction.txt
│   │   └── moore_trend/
│   │       ├── plot_moore_chronology.py
│   │       └── prediction_summary.txt
│   │
│   ├── plots/                  # Phase-III figures
│   ├── inclusion_latency_bench # Inclusion/exclusion benchmark
│   └── run_hazel_phase1.sh     # Hazel experiment launcher
│
└── README.md
