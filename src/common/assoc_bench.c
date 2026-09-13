#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define ITERATIONS 1000000UL
#define PAGE_SIZE 4096UL

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
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number_of_conflicting_lines>\n", argv[0]);
        return 1;
    }

    size_t n = strtoul(argv[1], NULL, 10);

    if (n < 1 || n > 64) {
        fprintf(stderr, "Number of lines must be between 1 and 64\n");
        return 1;
    }

    size_t total_size = n * PAGE_SIZE;
    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, PAGE_SIZE, total_size) != 0) {
        perror("posix_memalign");
        return 1;
    }

    /*
     * Each node is exactly one page apart.
     * Therefore every node has the same page offset.
     *
     * We link them into a randomized circular pointer chain
     * so accesses remain dependent while avoiding a simple
     * predictable access pattern.
     */
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

    for (size_t i = 0; i < n; i++) {
        size_t current = order[i];
        size_t next = order[(i + 1) % n];

        uintptr_t *current_node =
            (uintptr_t *)(memory + current * PAGE_SIZE);

        uintptr_t *next_node =
            (uintptr_t *)(memory + next * PAGE_SIZE);

        *current_node = (uintptr_t)next_node;
    }

    uintptr_t *p = (uintptr_t *)memory;

    /* Warm up the complete conflict set. */
    for (size_t i = 0; i < n * 100; i++)
        p = (uintptr_t *)(*p);

    uint64_t start = read_timer_start();

    for (uint64_t i = 0; i < ITERATIONS; i++)
        p = (uintptr_t *)(*p);

    uint64_t end = read_timer_end();

    uint64_t elapsed = end - start;

    printf("conflicting_lines=%zu\n", n);
    printf("iterations=%lu\n", ITERATIONS);
    printf("elapsed_timer_units=%lu\n", elapsed);
    printf("timer_units_per_access=%.4f\n",
           (double)elapsed / ITERATIONS);
    printf("final_index=%ld\n",
           (long)(((uint8_t *)p - memory) / PAGE_SIZE));

    free(order);
    free(memory);

    return 0;
}
