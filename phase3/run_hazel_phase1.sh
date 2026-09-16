#!/bin/bash
#SBATCH --job-name=cache_phase1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=phase3/slurm_%j.out
#SBATCH --error=phase3/slurm_%j.err

set -e

REPO="$HOME/Project-1-ECE-592"
cd "$REPO"

mkdir -p phase3/data/hazel

HOST=$(hostname)
CPU_MODEL=$(lscpu | awk -F: '/Model name/ {gsub(/^ +/, "", $2); print $2; exit}')
ARCH=$(uname -m)

# Make a filesystem-safe machine name
MACHINE=$(echo "$CPU_MODEL" | tr ' /[]()@' '_' | tr -s '_')

OUT="phase3/data/hazel/${MACHINE}"
mkdir -p "$OUT"

echo "========================================"
echo "Hazel Phase-I cache experiment"
echo "========================================"
echo "Hostname:      $HOST"
echo "CPU:           $CPU_MODEL"
echo "Architecture:  $ARCH"
echo "Job ID:         $SLURM_JOB_ID"
echo "Node:           $SLURMD_NODENAME"
echo "Constraint:     $SLURM_JOB_CONSTRAINT"
echo "Output:         $OUT"
echo "Date:           $(date -Iseconds)"
echo "========================================"

# --------------------------------------------------
# Record complete machine information
# --------------------------------------------------

{
    echo "hostname=$HOST"
    echo "cpu_model=$CPU_MODEL"
    echo "architecture=$ARCH"
    echo "job_id=$SLURM_JOB_ID"
    echo "slurm_node=$SLURMD_NODENAME"
    echo "constraint=$SLURM_JOB_CONSTRAINT"
    echo "date=$(date -Iseconds)"
    echo
    lscpu
} > "$OUT/machine_info.txt"

# --------------------------------------------------
# Compile the EXISTING project implementations
# --------------------------------------------------

gcc -O0 -Wall -Wextra \
    src/common/benchmark.c \
    src/x86_64/timing.c \
    -o phase3/benchmark

gcc -O0 -Wall -Wextra \
    src/common/line_size_bench.c \
    src/x86_64/timing.c \
    -o phase3/line_size_bench

gcc -O0 -Wall -Wextra \
    src/common/assoc_bench.c \
    src/x86_64/timing.c \
    -o phase3/assoc_bench

gcc -O0 -Wall -Wextra \
    src/common/latency_bench.c \
    src/x86_64/timing.c \
    -o phase3/latency_bench

gcc -O0 -Wall -Wextra \
    src/common/inclusion_latency_bench.c \
    src/x86_64/timing.c \
    -o phase3/inclusion_latency_bench

# --------------------------------------------------
# 1. CACHE CAPACITY / HIERARCHY
# 1,000,000 iterations per point
# --------------------------------------------------

echo "=== CAPACITY SWEEP ==="

for size in \
    4096 8192 16384 32768 65536 131072 \
    262144 524288 1048576 2097152 4194304 8388608 \
    16777216 33554432 67108864 134217728
do
    echo "capacity $size"

    srun --cpu-bind=cores ./phase3/benchmark "$size" \
        > "$OUT/capacity_${size}.txt"
done

# Dense sweep around the L2-scale region.
# Same dense range used for the original Hazel experiment.

for size in \
    524288 557056 589824 622592 655360 688128 \
    720896 753664 786432 819200 851968 884736 \
    917504 950272 983040 1015808 1048576 \
    1114112 1179648 1245184 1310720 1376256 \
    1441792 1507328 1572864 1638400 1703936 \
    1769472 1835008 1900544 1966080 2031616 2097152
do
    echo "capacity_dense $size"

    srun --cpu-bind=cores ./phase3/benchmark "$size" \
        > "$OUT/capacity_dense_${size}.txt"
done

# --------------------------------------------------
# 2. CACHE LINE SIZE
#
# line_size_bench requires:
#     ./line_size_bench <offset_bytes>
#
# 1,000,000 trials per offset.
# --------------------------------------------------

echo "=== LINE SIZE SWEEP ==="

for offset in \
    16 24 32 40 48 56 64 72 80 88 96 104 112 120 128 144 160 192 224
do
    echo "line_size offset $offset"

    srun --cpu-bind=cores ./phase3/line_size_bench "$offset" \
        > "$OUT/line_size_${offset}.txt"
done

# --------------------------------------------------
# 3. ASSOCIATIVITY
#
# assoc_bench requires:
#     ./assoc_bench <number_of_conflicting_lines>
#
# --------------------------------------------------

echo "=== ASSOCIATIVITY SWEEP ==="

for lines in \
    1 2 3 4 5 6 7 8 9 10 12 16 24 32 48 64
do
    echo "associativity $lines"

    srun --cpu-bind=cores ./phase3/assoc_bench "$lines" \
        > "$OUT/assoc_${lines}.txt"
done

# --------------------------------------------------
# 4. HIT / NEXT-LEVEL LATENCY
#
# latency_bench requires:
#     ./latency_bench <working_set_bytes>
#
# --------------------------------------------------

echo "=== LATENCY SWEEP ==="

for size in \
    32768 65536 131072 262144 524288 \
    1048576 2097152 4194304 8388608 \
    16777216 33554432 67108864 134217728
do
    echo "latency $size"

    srun --cpu-bind=cores ./phase3/latency_bench "$size" \
        > "$OUT/latency_${size}.txt"
done

# --------------------------------------------------
# 5. INCLUSION / EXCLUSION
#
# inclusion_latency_bench requires:
#     ./inclusion_latency_bench <eviction_rounds>
#
# Timing-only evidence; no policy will be assumed.
# --------------------------------------------------

echo "=== INCLUSION / EXCLUSION SWEEP ==="

for rounds in 64 128 256 512 1024
do
    echo "inclusion rounds $rounds"

    srun --cpu-bind=cores ./phase3/inclusion_latency_bench "$rounds" \
        > "$OUT/inclusion_${rounds}.txt"
done

echo
echo "========================================"
echo "PHASE-I COMPLETE"
echo "========================================"
echo "Machine: $HOST"
echo "CPU:     $CPU_MODEL"
echo "Output:  $OUT"
echo "========================================"
