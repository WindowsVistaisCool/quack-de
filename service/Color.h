#pragma once

#include <cstdint>
#include "LEDMath8.h"
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

    // HSV to RGB conversion
    // h: 0-360, s: 0-1, v: 0-1
    static Color fromHSV(float h, float s, float v) {
        float r_f, g_f, b_f;

        int i = static_cast<int>(h / 60.0f) % 6;
        float f = (h / 60.0f) - i;
        float p = v * (1.0f - s);
        float q = v * (1.0f - f * s);
        float t = v * (1.0f - (1.0f - f) * s);

        switch (i) {
            case 0: r_f = v; g_f = t; b_f = p; break;
            case 1: r_f = q; g_f = v; b_f = p; break;
            case 2: r_f = p; g_f = v; b_f = t; break;
            case 3: r_f = p; g_f = q; b_f = v; break;
            case 4: r_f = t; g_f = p; b_f = v; break;
            case 5: r_f = v; g_f = p; b_f = q; break;
            default: r_f = g_f = b_f = 0; break;
        }

        return Color(
            static_cast<uint8_t>(std::clamp(r_f * 255.0f, 0.0f, 255.0f)),
            static_cast<uint8_t>(std::clamp(g_f * 255.0f, 0.0f, 255.0f)),
            static_cast<uint8_t>(std::clamp(b_f * 255.0f, 0.0f, 255.0f))
        );
    }

    uint8_t getAverageLight() {
        uint8_t avg = scale8(r, 85) +
                    scale8(g, 85) +
                    scale8(b, 85);
        return avg;
    }

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

// Blend two Colors using per-channel blend8 helper from LEDMath8
inline Color blend(const Color& c1, const Color& c2, uint8_t amountC2)
{
    Color result;
    result.r = blend8(c1.r, c2.r, amountC2);
    result.g = blend8(c1.g, c2.g, amountC2);
    result.b = blend8(c1.b, c2.b, amountC2);
    return result;
}

// HeatColor moved here because it depends on Color
inline Color HeatColor(uint8_t temperature)
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
