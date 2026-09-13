#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>

#define ITERATIONS 1000000UL
#define BATCH_SIZE 1000UL
#define L1_EVICT_LINES 12
#define TARGET_MAX 16

static inline uint64_t read_timer_start(void)
{
    uint32_t lo, hi;

    asm volatile(
        "lfence\n\t"
        "rdtsc\n\t"
        : "=a"(lo), "=d"(hi)
        :
        : "memory");

    return ((uint64_t)hi << 32) | lo;
}

static inline uint64_t read_timer_end(void)
{
    uint32_t lo, hi;

    asm volatile(
        "rdtscp\n\t"
        "lfence\n\t"
        : "=a"(lo), "=d"(hi)
        :
        : "rcx", "memory");

    return ((uint64_t)hi << 32) | lo;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr,
                "Usage: %s <target_lines> <target_stride_bytes>\n",
                argv[0]);
        return 1;
    }

    size_t target_lines = strtoul(argv[1], NULL, 10);
    size_t target_stride = strtoul(argv[2], NULL, 10);

    if (target_lines < 1 || target_lines > TARGET_MAX) {
        fprintf(stderr, "target_lines must be 1-%d\n", TARGET_MAX);
        return 1;
    }

    if (target_stride < 4096 || target_stride % 64 != 0) {
        fprintf(stderr,
                "target_stride must be >=4096 and a multiple of 64\n");
        return 1;
    }

    /*
     * The target addresses are separated by the requested stride.
     * We test 8 KiB and 16 KiB because these spacings produced
     * interesting transitions in the earlier exploratory sweep.
     */
    size_t target_size = target_lines * target_stride;

    /*
     * Eviction addresses are placed after the target region.
     * A 4 KiB stride gives different higher address bits while
     * preserving the same L1 set-index bits.
     */
    size_t evict_stride = 4096;
    size_t evict_base = target_size + 4096;

    size_t total_size =
        evict_base + L1_EVICT_LINES * evict_stride + 4096;

    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, 4096, total_size) != 0) {
        perror("posix_memalign");
        return 1;
    }

    madvise(memory, total_size, MADV_HUGEPAGE);

    uintptr_t **targets =
        malloc(target_lines * sizeof(uintptr_t *));

    uintptr_t **evict =
        malloc(L1_EVICT_LINES * sizeof(uintptr_t *));

    if (targets == NULL || evict == NULL) {
        perror("malloc");
        free(targets);
        free(evict);
        free(memory);
        return 1;
    }

    /*
     * Target pointer chain.
     */
    for (size_t i = 0; i < target_lines; i++) {

        uintptr_t *current =
            (uintptr_t *)(memory + i * target_stride);

        uintptr_t *next =
            (uintptr_t *)(memory +
                          ((i + 1) % target_lines) * target_stride);

        *current = (uintptr_t)next;
        targets[i] = current;
    }

    /*
     * L1 eviction pointer chain.
     */
    for (size_t i = 0; i < L1_EVICT_LINES; i++) {

        uintptr_t *current =
            (uintptr_t *)(memory +
                          evict_base +
                          i * evict_stride);

        uintptr_t *next =
            (uintptr_t *)(memory +
                          evict_base +
                          ((i + 1) % L1_EVICT_LINES) *
                          evict_stride);

        *current = (uintptr_t)next;
        evict[i] = current;
    }

    /*
     * Warm up.
     */
    uintptr_t *p = targets[0];

    for (size_t i = 0; i < target_lines * 100; i++) {
        p = (uintptr_t *)(*p);
    }

    uintptr_t *e = evict[0];

    for (size_t i = 0; i < L1_EVICT_LINES * 100; i++) {
        e = (uintptr_t *)(*e);
    }

    const size_t batches = ITERATIONS / BATCH_SIZE;

    uint64_t total_with_target = 0;
    uint64_t total_eviction_only = 0;

    /*
     * Measurement 1:
     *
     * L1 eviction traversal followed by one dependent target load.
     */
    p = targets[0];

    for (size_t batch = 0; batch < batches; batch++) {

        uint64_t start = read_timer_start();

        for (size_t i = 0; i < BATCH_SIZE; i++) {

            e = evict[0];

            for (size_t j = 0; j < L1_EVICT_LINES; j++) {
                e = (uintptr_t *)(*e);
            }

            p = (uintptr_t *)(*p);
        }

        uint64_t end = read_timer_end();

        total_with_target += end - start;
    }

    /*
     * Measurement 2:
     *
     * Same eviction traversal, but without the target load.
     */
    e = evict[0];

    for (size_t batch = 0; batch < batches; batch++) {

        uint64_t start = read_timer_start();

        for (size_t i = 0; i < BATCH_SIZE; i++) {

            e = evict[0];

            for (size_t j = 0; j < L1_EVICT_LINES; j++) {
                e = (uintptr_t *)(*e);
            }
        }

        uint64_t end = read_timer_end();

        total_eviction_only += end - start;
    }

    asm volatile("" :: "r"(p), "r"(e) : "memory");

    double with_target =
        (double)total_with_target / ITERATIONS;

    double eviction_only =
        (double)total_eviction_only / ITERATIONS;

    double estimated_target =
        with_target - eviction_only;

    printf("target_lines=%zu\n", target_lines);
    printf("target_stride_bytes=%zu\n", target_stride);
    printf("l1_evict_lines=%d\n", L1_EVICT_LINES);
    printf("l1_evict_stride_bytes=%zu\n", evict_stride);
    printf("iterations=%lu\n", ITERATIONS);
    printf("batch_size=%lu\n", BATCH_SIZE);
    printf("total_with_target=%lu\n", total_with_target);
    printf("total_eviction_only=%lu\n", total_eviction_only);
    printf("with_target_units_per_access=%.4f\n", with_target);
    printf("eviction_only_units_per_access=%.4f\n", eviction_only);
    printf("estimated_target_units_per_access=%.4f\n",
           estimated_target);

    free(targets);
    free(evict);
    free(memory);

    return 0;
}
