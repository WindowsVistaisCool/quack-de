#pragma once

#include <cstdint>
#include <algorithm>

struct Color {
    Color() : r(0), g(0), b(0) {}
    Color(uint8_t r, uint8_t g, uint8_t b) : r(r), g(g), b(b) {}
    Color(uint32_t color) {
        r = (color >> 16) & 0xFF;
        g = (color >> 8) & 0xFF;
        b = color & 0xFF;
    }

    uint8_t r, g, b;

    inline Color &operator|=(const Color &rhs) {
        if (rhs.r > r) r = rhs.r;
        if (rhs.g > g) g = rhs.g;
        if (rhs.b > b) b = rhs.b;
        return *this;
    }

    inline Color operator+(const Color &rhs) const {
        auto qadd8 = [](uint8_t a, uint8_t b) -> uint8_t {
            unsigned int t = a + b;
            if (t > 255) t = 255;
            return static_cast<uint8_t>(t);
        };
        return Color{qadd8(r, rhs.r), qadd8(g, rhs.g), qadd8(b, rhs.b)};
    }
};
