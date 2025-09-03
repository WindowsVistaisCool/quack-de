#pragma once

#include <cstdlib>
#include <cstdint>
#include <vector>
#include "LEDMath8.h"
#include "Color.h"

class Palette
{
public:
    Palette(const std::vector<Color> &colors) : m_colors(colors) {}

    Color getColor(uint8_t index) const
    {
        if (index < m_colors.size())
        {
            return m_colors[index];
        }
        return Color(0, 0, 0); // Return black if index is out of bounds
    }

    void setColor(uint8_t index, Color color)
    {
        if (index < m_colors.size())
        {
            m_colors[index] = color;
        }
    }

private:
    std::vector<Color> m_colors;
};

// Color-from-palette helper (uses helpers from LEDMath8)
inline Color ColorFromPalette(const Palette &pal, uint8_t index, uint8_t brightness, BLENDTYPE blendType)
{
    if (blendType == LINEARBLEND_NOWRAP) {
        return Color(0,0,0); // placeholder
    }

    uint8_t hi4 = index >> 4;
    uint8_t lo4 = index & 0x0F;

    uint8_t blend = lo4 && (blendType != NOBLEND);

    Color color1 = pal.getColor(hi4);
    uint8_t red1 = color1.r;
    uint8_t green1 = color1.g;
    uint8_t blue1 = color1.b;

    if (blend) {
        Color color2 = Color(0,0,0);
        if (hi4 == 15) {
            color2 = pal.getColor(0);
        } else {
            color2 = pal.getColor(hi4 + 1);
        }

        uint8_t f2 = lo4 << 4;
        uint8_t f1 = 255 - f2;

        red1 = scale8(red1, f1);
        uint8_t red2 = scale8(color2.r, f2);
        red1 += red2;

        green1 = scale8(green1, f1);
        uint8_t green2 = scale8(color2.g, f2);
        green1 += green2;

        blue1 = scale8(blue1, f1);
        uint8_t blue2 = scale8(color2.b, f2);
        blue1 += blue2;
    }

    if (brightness != 255) {
        if (brightness) {
            ++brightness;
            if (red1) {
                red1 = scale8(red1, brightness);
                ++red1;
            }
            if (green1) {
                green1 = scale8(green1, brightness);
                ++green1;
            }
            if (blue1) {
                blue1 = scale8(blue1, brightness);
                ++blue1;
            }
        } else {
            red1 = 0;
            green1 = 0;
            blue1 = 0;
        }
    }

    return Color(red1, green1, blue1);
}