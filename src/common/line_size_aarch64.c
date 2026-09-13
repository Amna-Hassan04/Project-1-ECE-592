#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "timing.h"

#define SAMPLES 1000000UL
#define CHAIN_LENGTH 1000UL

static uint8_t *build_chain(size_t footprint, size_t stride)
{
    size_t count = footprint / stride;
    size_t *order = malloc(count * sizeof(size_t));
    uint8_t *memory = NULL;

    if (!order || posix_memalign((void **)&memory, 64, footprint) != 0) {
        free(order);
        return NULL;
    }

    memset(memory, 0, footprint);

    for (size_t i = 0; i < count; i++)
        order[i] = i;

    srand(12345);

    for (size_t i = count - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);
        size_t tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }

    for (size_t i = 0; i < count; i++) {
        size_t current = order[i];
        size_t next = order[(i + 1) % count];
        *(uint8_t **)(memory + current * stride) =
            memory + next * stride;
    }

    free(order);
    return memory;
}

static inline uint8_t *dependent_loads(uint8_t *ptr)
{
    for (uint64_t i = 0; i < CHAIN_LENGTH; i++)
        ptr = *(uint8_t **)ptr;
    return ptr;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <footprint_bytes> <stride_bytes>\n", argv[0]);
        return 1;
    }

    size_t footprint = strtoull(argv[1], NULL, 10);
    size_t stride = strtoull(argv[2], NULL, 10);

    if (stride < 8 || footprint < stride || footprint % stride != 0) {
        fprintf(stderr, "Invalid footprint/stride\n");
        return 1;
    }

    uint8_t *memory = build_chain(footprint, stride);

    if (!memory) {
        perror("allocation");
        return 1;
    }

    uint8_t *ptr = memory;

    size_t count = footprint / stride;

    for (size_t i = 0; i < count; i++)
        ptr = *(uint8_t **)ptr;

    for (uint64_t sample = 0; sample < SAMPLES; sample++) {
        uint64_t start = read_timer_start();
        ptr = dependent_loads(ptr);
        uint64_t end = read_timer_end();
        printf("%lu\n", end - start);
    }

    asm volatile("" :: "r"(ptr) : "memory");

    free(memory);
    return 0;
}
