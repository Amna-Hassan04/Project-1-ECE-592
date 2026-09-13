#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "timing.h"

#define ITERATIONS 1000000UL

static void create_pointer_cycle(uint32_t *next, size_t n)
{
    size_t *indices = malloc(n * sizeof(size_t));

    if (indices == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    for (size_t i = 0; i < n; i++) {
        indices[i] = i;
    }

    srand(12345);

    for (size_t i = n - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);

        size_t temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
    }

    for (size_t i = 0; i < n - 1; i++) {
        next[indices[i]] = (uint32_t)indices[i + 1];
    }

    next[indices[n - 1]] = (uint32_t)indices[0];

    free(indices);
}

static uint32_t pointer_chase(
    const uint32_t *next,
    uint32_t index,
    uint64_t iterations)
{
    for (uint64_t i = 0; i < iterations; i++) {
        index = next[index];
    }

    return index;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <working_set_bytes>\n", argv[0]);
        return EXIT_FAILURE;
    }

    size_t array_size = strtoull(argv[1], NULL, 10);

    if (array_size < sizeof(uint32_t)) {
        fprintf(stderr, "Working set must be at least 4 bytes.\n");
        return EXIT_FAILURE;
    }

    size_t n = array_size / sizeof(uint32_t);

    uint32_t *next = NULL;

    if (posix_memalign((void **)&next, 64,
                       n * sizeof(uint32_t)) != 0) {
        perror("posix_memalign");
        return EXIT_FAILURE;
    }

    memset(next, 0, n * sizeof(uint32_t));

    create_pointer_cycle(next, n);

    /* Warm up */
    volatile uint32_t warmup_result =
        pointer_chase(next, 0, ITERATIONS);

    (void)warmup_result;

    uint32_t index = 0;

    uint64_t start = read_timer_start();

    index = pointer_chase(next, index, ITERATIONS);

    uint64_t end = read_timer_end();

    uint64_t elapsed = end - start;

    printf("Working set bytes: %zu\n", array_size);
    printf("Iterations: %lu\n", ITERATIONS);
    printf("Elapsed timer units: %lu\n", elapsed);
    printf("Timer units/access: %.4f\n",
           (double)elapsed / ITERATIONS);
    printf("Final index: %u\n", index);

    free(next);

    return 0;
}
