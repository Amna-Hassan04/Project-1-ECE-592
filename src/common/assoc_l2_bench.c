#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>

#define ITERATIONS 1000000UL
#define MAX_LINES 32

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
                "Usage: %s <number_of_lines> <stride_bytes>\n",
                argv[0]);
        return 1;
    }

    size_t n = strtoul(argv[1], NULL, 10);
    size_t stride = strtoul(argv[2], NULL, 10);

    if (n < 1 || n > MAX_LINES) {
        fprintf(stderr, "Number of lines must be between 1 and %d\n",
                MAX_LINES);
        return 1;
    }

    if (stride < 4096 || stride > 131072 ||
        (stride & (stride - 1)) != 0) {
        fprintf(stderr,
                "Stride must be a power of two between 4096 and 131072 bytes\n");
        return 1;
    }

    size_t total_size = n * stride;

    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, 4096, total_size) != 0) {
        perror("posix_memalign");
        return 1;
    }

    /*
     * Ask Linux to prefer transparent huge pages.
     * This reduces the chance that page-walk/TLB effects dominate
     * the conflict experiment. The request is only a hint.
     */
    madvise(memory, total_size, MADV_HUGEPAGE);

    size_t *order = malloc(n * sizeof(size_t));

    if (order == NULL) {
        perror("malloc");
        free(memory);
        return 1;
    }

    for (size_t i = 0; i < n; i++)
        order[i] = i;

    srand(12345);

    for (size_t i = n - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);

        size_t temp = order[i];
        order[i] = order[j];
        order[j] = temp;
    }

    /*
     * Create a randomized circular dependent pointer chain.
     * Every node is separated by exactly 'stride' bytes.
     */
    for (size_t i = 0; i < n; i++) {
        size_t current = order[i];
        size_t next = order[(i + 1) % n];

        uintptr_t *current_node =
            (uintptr_t *)(memory + current * stride);

        uintptr_t *next_node =
            (uintptr_t *)(memory + next * stride);

        *current_node = (uintptr_t)next_node;
    }

    uintptr_t *p = (uintptr_t *)memory;

    /*
     * Warm the complete chain so that the measurement starts
     * after initial compulsory misses.
     */
    for (size_t i = 0; i < n * 100; i++)
        p = (uintptr_t *)(*p);

    uint64_t start = read_timer_start();

    for (uint64_t i = 0; i < ITERATIONS; i++)
        p = (uintptr_t *)(*p);

    uint64_t end = read_timer_end();

    uint64_t elapsed = end - start;

    printf("conflicting_lines=%zu\n", n);
    printf("stride_bytes=%zu\n", stride);
    printf("working_set_bytes=%zu\n", total_size);
    printf("iterations=%lu\n", ITERATIONS);
    printf("elapsed_timer_units=%lu\n", elapsed);
    printf("timer_units_per_access=%.4f\n",
           (double)elapsed / ITERATIONS);

    free(order);
    free(memory);

    return 0;
}
