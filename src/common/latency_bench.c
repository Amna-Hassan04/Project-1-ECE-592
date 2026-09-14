#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "timing.h"

#define SAMPLES 1000000UL
#define CHAIN_LENGTH 1000UL



/*
 * Perform 1000 dependent loads.
 * Each load produces the address used by the next load.
 */
static inline uint8_t *dependent_loads(uint8_t *ptr)
{
    for (uint64_t i = 0; i < CHAIN_LENGTH; i++) {
        ptr = *(uint8_t **)ptr;
    }

    return ptr;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <working_set_bytes>\n", argv[0]);
        return 1;
    }

    size_t size = strtoull(argv[1], NULL, 10);

    if (size < 64 || size > (256UL * 1024 * 1024)) {
        fprintf(stderr, "Working set must be between 64 B and 256 MiB\n");
        return 1;
    }

    /*
     * Use one pointer per 64-byte cache-line-sized region.
     */
    size_t lines = (size + 63) / 64;
    size_t alloc_size = lines * 64;

    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, 64, alloc_size) != 0) {
        perror("posix_memalign");
        return 1;
    }

    memset(memory, 0, alloc_size);

    /*
     * Create an array of line indices that we will shuffle.
     */
    size_t *order = malloc(lines * sizeof(size_t));

    if (order == NULL) {
        perror("malloc");
        free(memory);
        return 1;
    }

    for (size_t i = 0; i < lines; i++) {
        order[i] = i;
    }

    /*
     * Fixed seed makes the experiment reproducible.
     */
    srand(12345);

    /*
     * Fisher-Yates shuffle.
     */
    for (size_t i = lines - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);

        size_t temp = order[i];
        order[i] = order[j];
        order[j] = temp;
    }

    /*
     * Build the randomized circular pointer chain.
     */
    for (size_t i = 0; i < lines; i++) {

        size_t current = order[i];
        size_t next = order[(i + 1) % lines];

        *(uint8_t **)(memory + current * 64) =
            memory + next * 64;
    }

    uint8_t *ptr = memory + order[0] * 64;

    /*
     * Warm up the working set.
     */
    for (size_t i = 0; i < lines; i++) {
        ptr = *(uint8_t **)ptr;
    }

    /*
     * Each sample measures 1000 dependent loads.
     */
    for (uint64_t sample = 0; sample < SAMPLES; sample++) {

        uint64_t start = read_timer_start();

        ptr = dependent_loads(ptr);

        uint64_t end = read_timer_end();

        printf("%lu\n", end - start);
    }

    /*
     * Prevent the compiler from treating ptr as unused.
     */

    free(order);
    free(memory);

    return 0;
}
