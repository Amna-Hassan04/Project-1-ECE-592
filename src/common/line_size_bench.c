#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TRIALS 1000000UL

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

static inline void flush_line(void *addr)
{
    asm volatile("clflush (%0)" :: "r"(addr) : "memory");
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <offset_bytes>\n", argv[0]);
        return 1;
    }

    size_t offset = strtoul(argv[1], NULL, 10);

    if (offset == 0 || offset >= 256) {
        fprintf(stderr, "Offset must be between 1 and 255 bytes\n");
        return 1;
    }

    uint8_t *memory = NULL;

    if (posix_memalign((void **)&memory, 64, 512) != 0) {
        perror("posix_memalign");
        return 1;
    }

    memset(memory, 0, 512);

    /*
     * Store the address of the second location at the base.
     * The first load retrieves this pointer; the second load
     * is therefore dependent on the first.
     */
    uint8_t **base_ptr = (uint8_t **)memory;
    volatile uint8_t *second = memory + offset;

    *base_ptr = (uint8_t *)second;
    *second = 1;

    for (uint64_t trial = 0; trial < TRIALS; trial++) {

        flush_line((void *)memory);
        flush_line((void *)second);
        asm volatile("mfence" ::: "memory");

        uint64_t start = read_timer_start();

        uint8_t *p;
        uint8_t value;

        asm volatile(
            "mov (%1), %0\n\t"
            "mov (%0), %2\n\t"
            : "=&r"(p), "=&r"(base_ptr), "=&r"(value)
            : "1"(base_ptr)
            : "memory");

        uint64_t end = read_timer_end();

        asm volatile("" :: "r"(value) : "memory");

        printf("%lu\n", end - start);
    }

    free(memory);
    return 0;
}
