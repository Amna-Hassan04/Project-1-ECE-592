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
│
├── src/
│   ├── common/
│   │   ├── benchmark.c
│   │   └── timing.h
│   │
│   ├── x86_64/
│   │   └── timing.c
│   │
│   └── aarch64/
│       └── timing.c
│
├── experiments/
│   └── capacity/
│       └── run_sweep.sh
│
├── data/
│   ├── sunbird/ 
│   ├── thunderbird/
│   ├── skylark/
│   ├── artemisia/
│   ├── charnwood/
│   ├── crux/
│   ├── upgrade/
│   └── ookay/
│
├── analysis/
│   └── ...
│
├── phase3/
│   ├── data/
│   ├── predictions/
│   ├── plots/
│   ├── analysis/
│   └── report_data/
│
└── README.md
