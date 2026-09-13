#include <stdint.h>

uint64_t read_timer_start(void)
{
    uint32_t lo;
    uint32_t hi;

    asm volatile(
        "lfence\n\t"
        "rdtsc\n\t"
        : "=a"(lo), "=d"(hi)
        :
        : "memory"
    );

    return ((uint64_t)hi << 32) | lo;
}

uint64_t read_timer_end(void)
{
    uint32_t lo;
    uint32_t hi;

    asm volatile(
        "rdtscp\n\t"
        "lfence\n\t"
        : "=a"(lo), "=d"(hi)
        :
        : "rcx", "memory"
    );

    return ((uint64_t)hi << 32) | lo;
}
