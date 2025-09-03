#pragma once

#include <cstdint>
#include <cstdlib>
#include "PixelStrip.h"

uint8_t random8(uint8_t min, uint8_t max)
{
    return rand() % (max - min + 1) + min;
}

uint8_t random8(uint8_t lim) {
    uint8_t r = random8(0, 255);
    r = (r * lim) >> 8;
    return r;
}

uint8_t qadd8(uint8_t a, uint8_t b)
{
    unsigned int t = a + b;
    if (t > 255)
        t = 255;
    return t;
}

uint8_t qsub8(uint8_t a, uint8_t b)
{
    int t = a - b;
    if (t < 0)
        t = 0;
    return t;
}

uint8_t scale8(uint8_t i, uint8_t scale)
{
    return (((uint16_t)(i)) * ((uint16_t)(scale + 1))) >> 8;
}

Color HeatColor(uint8_t temperature)
{
    Color c = Color{0, 0, 0};

    uint8_t scaled = scale8(temperature, 191);

    uint8_t heatramp = scaled & 0x3F; // 0..63
    heatramp <<= 2;

    if (scaled & 0x80) {
        c.r = 255;
        c.g = 255;
        c.b = heatramp;
    } else if (scaled & 0x40) {
        c.r = 255;
        c.g = heatramp;
        c.b = 0;
    } else {
        c.r = heatramp;
        c.g = 0;
        c.b = 0;
    }

    return c;
}