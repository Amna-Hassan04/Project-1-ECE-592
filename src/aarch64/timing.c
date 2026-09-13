#include <stdint.h>
#include <arm_acle.h>
#include "../common/timing.h"

static inline uint64_t read_cntvct(void)
{
    uint64_t value;
    asm volatile("isb\n\tmrs %0, cntvct_el0" : "=r"(value) :: "memory");
    return value;
}

uint64_t read_timer_start(void)
{
    return read_cntvct();
}

uint64_t read_timer_end(void)
{
    uint64_t value;
    asm volatile("mrs %0, cntvct_el0\n\tisb" : "=r"(value) :: "memory");
    return value;
}
