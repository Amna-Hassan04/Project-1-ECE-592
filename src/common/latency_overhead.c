#include <stdint.h>
#include <stdio.h>

#define SAMPLES 10000UL

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

int main(void)
{
    volatile uint64_t value = 0;

    for (uint64_t sample = 0; sample < SAMPLES; sample++) {

        uint64_t start = read_timer_start();

        /*
         * Control operation: no memory-dependent load.
         * This lets us estimate the fixed timing-measurement overhead.
         */
        value++;

        uint64_t end = read_timer_end();

        printf("%lu\n", end - start);
    }

    return (int)(value & 0);
}
