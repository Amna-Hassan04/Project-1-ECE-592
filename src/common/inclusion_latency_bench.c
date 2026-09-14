#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "timing.h"

#define SAMPLES 1000000UL
#define RELOADS 1000UL
#define EVICT_LINES 32UL
#define LINE_SIZE 64UL
#define PAGE_SIZE 4096UL

/*
 * Target line is repeatedly loaded into the upper cache.
 *
 * The eviction region provides lower-level cache pressure.
 * We compare target reload latency with and without that
 * pressure. Because cache-set mapping is not directly known
 * in Phase I, the result is treated as timing evidence and
 * not as a definitive inclusion/exclusion classification.
 */

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr,
                "Usage: %s <eviction_rounds>\n", argv[0]);
        return 1;
    }

    size_t eviction_rounds = strtoul(argv[1], NULL, 10);

    size_t target_size = PAGE_SIZE;
    size_t eviction_size = EVICT_LINES * PAGE_SIZE;

    uint8_t *target_mem = NULL;
    uint8_t *evict_mem = NULL;

    if (posix_memalign((void **)&target_mem,
                       PAGE_SIZE, target_size) != 0) {
        perror("posix_memalign target");
        return 1;
    }

    if (posix_memalign((void **)&evict_mem,
                       PAGE_SIZE, eviction_size) != 0) {
        perror("posix_memalign eviction");
        free(target_mem);
        return 1;
    }

    /*
     * Target is one cache line.
     */
    volatile uint64_t *target =
        (volatile uint64_t *)target_mem;

    *target = 0x12345678ULL;

    /*
     * Eviction addresses are page spaced.
     */
    volatile uint64_t **evict_nodes =
        malloc(EVICT_LINES * sizeof(*evict_nodes));

    if (evict_nodes == NULL) {
        perror("malloc");
        free(target_mem);
        free(evict_mem);
        return 1;
    }

    for (size_t i = 0; i < EVICT_LINES; i++) {
        evict_nodes[i] =
            (volatile uint64_t *)(evict_mem + i * PAGE_SIZE);

        *evict_nodes[i] = (uint64_t)i;
    }

    /*
     * Warm up target and eviction region.
     */
    for (size_t i = 0; i < RELOADS; i++)
        (void)*target;

    for (size_t r = 0; r < eviction_rounds; r++) {
        for (size_t i = 0; i < EVICT_LINES; i++)
            (void)*evict_nodes[i];
    }

    for (uint64_t sample = 0; sample < SAMPLES; sample++) {

        /*
         * First establish the target in the upper cache.
         */
        for (size_t i = 0; i < RELOADS; i++)
            (void)*target;

        /*
         * Apply controlled lower-level cache pressure.
         */
        for (size_t r = 0; r < eviction_rounds; r++) {
            for (size_t i = 0; i < EVICT_LINES; i++)
                (void)*evict_nodes[i];
        }

        /*
         * Measure dependent target loads after pressure.
         */
        uint64_t start = read_timer_start();

        volatile uint64_t value = 0;

        for (size_t i = 0; i < RELOADS; i++)
            value += *target;

        uint64_t end = read_timer_end();

        (void)value;

        printf("%lu\n", end - start);
    }

    free(evict_nodes);
    free(target_mem);
    free(evict_mem);

    return 0;
}
