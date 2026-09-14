#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "timing.h"

#define SAMPLES 1000000UL
#define CHAIN_LENGTH 1000UL
#define PAGE_SIZE 4096UL

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number_of_conflicting_lines>\n", argv[0]);
        return 1;
    }

    size_t n = strtoul(argv[1], NULL, 10);

    if (n < 1 || n > 32) {
        fprintf(stderr, "Number of conflicting lines must be 1-32\n");
        return 1;
    }

    size_t total_size = n * PAGE_SIZE;
    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, PAGE_SIZE, total_size) != 0) {
        perror("posix_memalign");
        return 1;
    }

    /*
     * Page-spaced addresses have the same page offset.
     * They are used as an L1 conflict-set probe.
     */
    uintptr_t **nodes = malloc(n * sizeof(uintptr_t *));

    if (nodes == NULL) {
        perror("malloc");
        free(memory);
        return 1;
    }

    for (size_t i = 0; i < n; i++)
        nodes[i] = (uintptr_t *)(memory + i * PAGE_SIZE);

    for (size_t i = 0; i < n; i++)
        *nodes[i] = (uintptr_t)nodes[(i + 1) % n];

    volatile uintptr_t *p = nodes[0];

    /* Warm up the conflict chain. */
    for (size_t i = 0; i < n * 100; i++)
        p = (uintptr_t *)(*p);

    for (uint64_t sample = 0; sample < SAMPLES; sample++) {

        uint64_t start = read_timer_start();

        for (size_t i = 0; i < CHAIN_LENGTH; i++)
            p = (uintptr_t *)(*p);

        uint64_t end = read_timer_end();

        printf("%lu\n", end - start);
    }

    /*
     * Prevent the compiler from treating p as dead.
     */
    fprintf(stderr, "final_node=%ld\n",
            (long)(((uint8_t *)p - memory) / PAGE_SIZE));

    free(nodes);
    free(memory);

    return 0;
}
