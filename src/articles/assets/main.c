#include <inttypes.h>
#include <stdio.h>

__attribute__((weak)) int8_t number;

int main() { printf("Size : %d.\n", sizeof(number));main(); }