#pragma once

#include <cstdint>
#include <vector>
#include "ws2811.h"

struct Color
{
    uint8_t r, g, b;
};

class PixelStrip
{
public:
    PixelStrip(int count, int gpio = 18, int dma = 10, int freq = WS2811_TARGET_FREQ, int channel = 0);
    ~PixelStrip();

    bool begin();

    void setBrightness(uint8_t brightness);

    void setPixelColor(int index, const Color& color);
    void setPixelColor(int index, uint8_t r, uint8_t g, uint8_t b);
    void show();

    uint32_t getRawPixelColor(int index);
    Color getPixelColor(int index);

    void clear();

    int numPixels() const { return m_count; }

private:
    ws2811_t m_leds;
    int m_count;
    int m_channel;
};
