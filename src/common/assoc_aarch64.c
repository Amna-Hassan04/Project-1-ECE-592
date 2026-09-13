#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "timing.h"

#define ITERATIONS 1000000UL
#define PAGE_SIZE 4096UL

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number_of_conflicting_lines>\n", argv[0]);
        return 1;
    }

    size_t n = strtoull(argv[1], NULL, 10);

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

    size_t *order = malloc(n * sizeof(size_t));

    if (!order) {
        perror("malloc");
        free(memory);
        return 1;
    }

    for (size_t i = 0; i < n; i++)
        order[i] = i;

    srand(12345);

    for (size_t i = n - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);
        size_t tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
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

    free(order);
    free(memory);

    return 0;
}
