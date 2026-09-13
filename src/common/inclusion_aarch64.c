#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "timing.h"

#define SAMPLES 1000000UL
#define TARGET_LINES 1000UL
#define LINE_SIZE 64UL
#define EVICTION_STRIDE 64UL
#define RELOADS 1000UL

static inline uint8_t *dependent_loads(uint8_t *ptr)
{
    for (uint64_t i = 0; i < RELOADS; i++)
        ptr = *(uint8_t **)ptr;

    return ptr;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <eviction_footprint_bytes>\n", argv[0]);
        return 1;
    }

    size_t footprint = strtoull(argv[1], NULL, 10);

    if (footprint < 4096 || footprint > (128UL * 1024 * 1024)) {
        fprintf(stderr, "Footprint must be between 4 KiB and 128 MiB\n");
        return 1;
    }

    size_t target_size = TARGET_LINES * LINE_SIZE;

    uint8_t *target = NULL;
    uint8_t *eviction = NULL;

    if (posix_memalign((void **)&target, 64, target_size) != 0 ||
        posix_memalign((void **)&eviction, 64, footprint) != 0) {
        perror("posix_memalign");
        free(target);
        free(eviction);
        return 1;
    }

    memset(target, 0, target_size);
    memset(eviction, 1, footprint);

    /*
     * Build a dependent circular chain through the target lines.
     */
    for (size_t i = 0; i < TARGET_LINES; i++) {
        size_t next = (i + 1) % TARGET_LINES;
        *(uint8_t **)(target + i * LINE_SIZE) =
            target + next * LINE_SIZE;
    }

    uint8_t *ptr = target;

    /*
     * Warm the target chain.
     */
    for (size_t i = 0; i < TARGET_LINES * 10; i++)
        ptr = *(uint8_t **)ptr;

    for (uint64_t sample = 0; sample < SAMPLES; sample++) {

        /*
         * Eviction pressure. The target array is never touched here.
         */
        for (size_t offset = 0;
             offset < footprint;
             offset += EVICTION_STRIDE) {

            volatile uint8_t value = eviction[offset];
            (void)value;
        }

        uint64_t start = read_timer_start();

        ptr = dependent_loads(ptr);

        uint64_t end = read_timer_end();

        printf("%lu\n", end - start);
    }

    asm volatile("" :: "r"(ptr) : "memory");

    free(target);
    free(eviction);

    return 0;
}
