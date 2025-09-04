#pragma once

#include <cstdint>
#include <cstdlib>
#include <cmath>
#include <chrono>
#include <cstdint>

enum BLENDTYPE {
    LINEARBLEND = 0,
    NOBLEND = 1,
    LINEARBLEND_NOWRAP = 2
};

inline uint8_t scale8(uint8_t i, uint8_t scale)
{
    return (((uint16_t)(i)) * ((uint16_t)(scale + 1))) >> 8;
}

// Types and helpers used by FastLED-style beat/sine functions
using accum88 = uint16_t; // Q8.8 fixed-point BPM value

// Milliseconds provider similar to Arduino millis(); uses steady_clock
inline uint32_t GET_MILLIS()
{
    using namespace std::chrono;
    return static_cast<uint32_t>(duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count());
}

// FastLED-style sin/scale helpers
// sin16: input 0..65535 -> output -32768..32767
inline int16_t sin16(uint16_t theta)
{
    const double TWO_PI = std::acos(-1.0) * 2.0;
    double angle = (static_cast<double>(theta) / 65536.0) * TWO_PI;
    double s = std::sin(angle);
    // map to full signed 16-bit range
    return static_cast<int16_t>(s * 32767.0);
}

// sin8: input 0..255 -> output 0..255 (0=center at 128)
inline uint8_t sin8(uint8_t theta)
{
    const double TWO_PI = std::acos(-1.0) * 2.0;
    double angle = (static_cast<double>(theta) / 256.0) * TWO_PI;
    double s = std::sin(angle); // -1..1
    double v = (s + 1.0) * 0.5 * 255.0;
    if (v < 0.0) v = 0.0;
    if (v > 255.0) v = 255.0;
    return static_cast<uint8_t>(v + 0.5);
}

// scale16: 16-bit scaling: (i * scale) >> 16
inline uint16_t scale16(uint16_t i, uint16_t scale)
{
    return static_cast<uint16_t>((static_cast<uint32_t>(i) * static_cast<uint32_t>(scale)) >> 16);
}

inline uint8_t blend8(uint8_t a, uint8_t b, uint8_t amountB) {
    uint8_t result;
    uint8_t amountA = 255 - amountB;
    result = scale8(a, amountA) + scale8(b, amountB);
    return result;
}

// Beat generators from FastLED (adapted)
inline uint16_t beat88(accum88 beats_per_minute_88, uint32_t timebase = 0)
{
    uint32_t ms = GET_MILLIS();
    uint32_t delta = ms - timebase;
    uint64_t v = static_cast<uint64_t>(delta) * static_cast<uint64_t>(beats_per_minute_88) * 280ULL;
    return static_cast<uint16_t>(v >> 16);
}

inline uint16_t beat16(accum88 beats_per_minute, uint32_t timebase = 0)
{
    if (beats_per_minute < 256) beats_per_minute = static_cast<accum88>(beats_per_minute << 8);
    return beat88(beats_per_minute, timebase);
}

inline uint8_t beat8(accum88 beats_per_minute, uint32_t timebase = 0)
{
    return static_cast<uint8_t>(beat16(beats_per_minute, timebase) >> 8);
}

inline uint16_t beatsin88(accum88 beats_per_minute_88, uint16_t lowest = 0, uint16_t highest = 65535,
                          uint32_t timebase = 0, uint16_t phase_offset = 0)
{
    uint16_t beat = beat88(beats_per_minute_88, timebase);
    int16_t s = sin16(static_cast<uint16_t>(beat + phase_offset));
    uint16_t beatsin = static_cast<uint16_t>(static_cast<uint16_t>(s + 32768));
    uint16_t rangewidth = highest - lowest;
    uint16_t scaledbeat = scale16(beatsin, rangewidth);
    uint16_t result = lowest + scaledbeat;
    return result;
}

inline uint16_t beatsin16(accum88 beats_per_minute, uint16_t lowest = 0, uint16_t highest = 65535,
                          uint32_t timebase = 0, uint16_t phase_offset = 0)
{
    // overload for accum88-based BPM; reuse beat16/sin16
    uint16_t beat = beat16(beats_per_minute, timebase);
    int16_t s = sin16(static_cast<uint16_t>(beat + phase_offset));
    uint16_t beatsin = static_cast<uint16_t>(static_cast<uint16_t>(s + 32768));
    uint16_t rangewidth = highest - lowest;
    uint16_t scaledbeat = scale16(beatsin, rangewidth);
    uint16_t result = lowest + scaledbeat;
    return result;
}

inline uint8_t beatsin8(accum88 beats_per_minute, uint8_t lowest = 0, uint8_t highest = 255,
                        uint32_t timebase = 0, uint8_t phase_offset = 0)
{
    uint8_t beat = beat8(beats_per_minute, timebase);
    uint8_t beatsin = sin8(static_cast<uint8_t>(beat + phase_offset));
    uint8_t rangewidth = highest - lowest;
    uint8_t scaledbeat = scale8(beatsin, rangewidth);
    uint8_t result = lowest + scaledbeat;
    return result;
}

inline uint8_t random8(uint8_t min, uint8_t max)
{
    return rand() % (max - min + 1) + min;
}

inline uint8_t random8(uint8_t lim) {
    uint8_t r = random8(0, 255);
    r = (r * lim) >> 8;
    return r;
}

inline uint8_t qadd8(uint8_t a, uint8_t b)
{
    unsigned int t = a + b;
    if (t > 255)
        t = 255;
    return t;
}

inline uint8_t qsub8(uint8_t a, uint8_t b)
{
    int t = a - b;
    if (t < 0)
        t = 0;
    return t;
}


