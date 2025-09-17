#pragma once

#include <cstdint>
#include "LEDMath8.h"
#include <algorithm>

struct HSVColor
{
    uint8_t h; // Hue (0-255)
    uint8_t s; // Saturation (0-255)
    uint8_t v; // Value (0-255)
};

struct Color
{
    Color() : r(0), g(0), b(0) {}
    Color(uint8_t r, uint8_t g, uint8_t b) : r(r), g(g), b(b) {}
    Color(uint32_t color)
    {
        r = (color >> 16) & 0xFF;
        g = (color >> 8) & 0xFF;
        b = color & 0xFF;
    }

    uint8_t r, g, b;

    // HSV to RGB conversion
    // h: 0-255, s: 0-255, v: 0-255
    static Color fromHSV(uint8_t h, uint8_t s, uint8_t v)
    {
        // Convert 0-255 hue to 0-360 degrees. Use 256 divisor so 255 maps just below 360
        float hf = (h / 256.0f) * 360.0f;
        float sf = s / 255.0f;
        float vf = v / 255.0f;

        float r_f = 0.0f, g_f = 0.0f, b_f = 0.0f;

        // sector 0..5
        int sector = static_cast<int>(std::floor(hf / 60.0f)) % 6;
        if (sector < 0)
            sector += 6;
        float f = (hf / 60.0f) - static_cast<float>(sector);
        float p = vf * (1.0f - sf);
        float q = vf * (1.0f - f * sf);
        float t = vf * (1.0f - (1.0f - f) * sf);

        switch (sector)
        {
        case 0:
            r_f = vf;
            g_f = t;
            b_f = p;
            break;
        case 1:
            r_f = q;
            g_f = vf;
            b_f = p;
            break;
        case 2:
            r_f = p;
            g_f = vf;
            b_f = t;
            break;
        case 3:
            r_f = p;
            g_f = q;
            b_f = vf;
            break;
        case 4:
            r_f = t;
            g_f = p;
            b_f = vf;
            break;
        case 5:
            r_f = vf;
            g_f = p;
            b_f = q;
            break;
        default:
            r_f = g_f = b_f = 0.0f;
            break;
        }

        return Color(
            static_cast<uint8_t>(std::clamp(r_f * 255.0f, 0.0f, 255.0f)),
            static_cast<uint8_t>(std::clamp(g_f * 255.0f, 0.0f, 255.0f)),
            static_cast<uint8_t>(std::clamp(b_f * 255.0f, 0.0f, 255.0f)));
    }

    static HSVColor toHSV(const Color &color)
    {
        uint8_t r = color.r;
        uint8_t g = color.g;
        uint8_t b = color.b;

        uint8_t max = std::max({r, g, b});
        uint8_t min = std::min({r, g, b});
        uint8_t v = max;
        uint8_t delta = max - min;
        uint8_t s = (max == 0) ? 0 : (delta * 255 / max);
        uint8_t h = 0;

        if (delta != 0)
        {
            // use signed arithmetic for intermediate hue to avoid unsigned wrap
            int hue = 0;
            if (max == r)
                hue = static_cast<int>(43) * (static_cast<int>(g) - static_cast<int>(b)) / static_cast<int>(delta);
            else if (max == g)
                hue = 85 + static_cast<int>(43) * (static_cast<int>(b) - static_cast<int>(r)) / static_cast<int>(delta);
            else
                hue = 171 + static_cast<int>(43) * (static_cast<int>(r) - static_cast<int>(g)) / static_cast<int>(delta);

            // wrap into 0..255 range (mod 256)
            int wrapped = (hue % 256);
            if (wrapped < 0)
                wrapped += 256;
            h = static_cast<uint8_t>(wrapped & 0xFF);
        }

        return HSVColor{h, s, v};
    }

    uint8_t getAverageLight()
    {
        uint8_t avg = scale8(r, 85) +
                      scale8(g, 85) +
                      scale8(b, 85);
        return avg;
    }

    inline Color &operator|=(const Color &rhs)
    {
        if (rhs.r > r)
            r = rhs.r;
        if (rhs.g > g)
            g = rhs.g;
        if (rhs.b > b)
            b = rhs.b;
        return *this;
    }

    inline Color operator+(const Color &rhs) const
    {
        auto qadd8 = [](uint8_t a, uint8_t b) -> uint8_t
        {
            unsigned int t = a + b;
            if (t > 255)
                t = 255;
            return static_cast<uint8_t>(t);
        };

        return Color{qadd8(r, rhs.r), qadd8(g, rhs.g), qadd8(b, rhs.b)};
    }
};

// Blend two Colors using per-channel blend8 helper from LEDMath8
inline Color blend(const Color &c1, const Color &c2, uint8_t amountC2)
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

    if (scaled & 0x80)
    {
        c.r = 255;
        c.g = 255;
        c.b = heatramp;
    }
    else if (scaled & 0x40)
    {
        c.r = 255;
        c.g = heatramp;
        c.b = 0;
    }
    else
    {
        c.r = heatramp;
        c.g = 0;
        c.b = 0;
    }

    return c;
}
