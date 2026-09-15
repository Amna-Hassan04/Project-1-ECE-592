# Phase II PMU Verification — OOKAY

## Machine
- CPU: Intel Core i7-7700
- Microarchitecture: Kaby Lake
- OS: Ubuntu 24.04.4
- Kernel: 6.8.0-100-generic
- Compiler: GCC 13.3.0
- Architecture: x86-64
- Physical cores: 4
- Logical CPUs: 8
- SMT: enabled
- NUMA nodes: 1

## Documented Cache Information
Obtained after Phase I:
- L1d: 32 KiB per core
- L1i: 32 KiB per core
- L2: 256 KiB per core
- L3: 8 MiB shared

`lscpu` reports aggregate cache capacity across the four cores:
- L1d: 128 KiB
- L1i: 128 KiB
- L2: 1 MiB
- L3: 8 MiB

## Phase-I Timing-Only Results
- L1 capacity: approximately 32 KiB
- L2 capacity: approximately 256 KiB (cautious)
- LLC transition: approximately 8–16 MiB
- Line size: approximately 64 B
- L1 associativity: approximately 8-way
- L1 sets: 64 derived sets
- Inclusion/exclusion: inconclusive

## PMU Validation Completed

### L2 validation
Events:
- `l2_rqsts.all_demand_references`
- `l2_rqsts.all_demand_miss`

| Footprint | L2 demand references | L2 demand misses |
|---|---:|---:|
| 16 KiB | 1,550,273 | 140,131 |
| 32 KiB | 281,602,362 | 190,895 |
| 64 KiB | 1,031,394,688 | 527,653 |
| 256 KiB | 1,034,735,888 | 416,167,048 |

Interpretation:
L2 activity increases strongly as the footprint exceeds the L1 scale. At 256 KiB, L2 demand misses increase substantially, providing independent PMU support for the Phase-I L2-scale inference. These counters are used as validation evidence rather than as the sole method for determining exact capacity.

### LLC validation
Events:
- `LLC-loads`
- `LLC-load-misses`

| Footprint | LLC loads | LLC load misses | Miss rate |
|---|---:|---:|---:|
| 4 MiB | 971,359,961 | 4,621,047 | 0.48% |
| 8 MiB | 1,020,208,181 | 272,906,293 | 26.75% |
| 16 MiB | 1,099,507,529 | 822,249,389 | 74.78% |
| 32 MiB | 1,193,432,449 | 937,753,640 | 78.58% |

Interpretation:
Timing-only measurements identified an LLC-scale transition between 8 and 16 MiB. PMU measurements independently show a strong increase in LLC-load miss rate from 0.48% at 4 MiB to 26.75% at 8 MiB and 74.78% at 16 MiB, consistent with the documented 8 MiB shared L3 cache.

## Generic PMU Sanity Check
Events:
- `cycles`
- `instructions`
- `cache-references`
- `cache-misses`

Recorded run:
- cycles: 20,763,587,645
- instructions: 12,268,464,896
- cache-references: 317,998,832
- cache-misses: 420,225
- elapsed time: 5.320344195 s
- user time: 3.651908 s
- system time: 1.439503 s

Generic cache events are treated only as a sanity check because their exact implementation semantics are less suitable for level-specific cache claims.

## Notes
- Each validation benchmark used the existing Phase-I benchmark with 1,000,000 samples.
- Phase-I inferred values remain unchanged.
- Raw PMU outputs should be preserved alongside processed tables.
- Exact PMU event names and semantics must be recorded for the final report.
