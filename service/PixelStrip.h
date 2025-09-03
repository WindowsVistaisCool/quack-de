#pragma once

#include <cstdint>
#include <vector>
#include "ws2811.h"

class PixelStrip
{
public:
    PixelStrip(int count, int gpio = 18, int dma = 10, int freq = WS2811_TARGET_FREQ, int channel = 0);
    ~PixelStrip();

    bool begin();

    void setBrightness(uint8_t brightness, bool log = false);

    void setPixelColor(int index, const Color &color);
    void setPixelColor(int index, uint8_t r, uint8_t g, uint8_t b);
    void show();

    uint32_t getRawPixelColor(int index);
    Color getPixelColor(int index);
    uint8_t getPixelAverageLight(int index);

    void clear();

    int numPixels() const { return m_count; }

    // Color operator[](int index) { return getPixelColor(index); }

    // struct PixelProxy {
    //     PixelStrip& strip;
    //     int index;
    //     PixelProxy& operator=(const Color& color) {
    //         strip.setPixelColor(index, color);
    //         return *this;
    //     }
    //     operator Color() const {
    //         return strip.getPixelColor(index);
    //     }
    // };
    // PixelProxy operator[](int index) {
    //     return PixelProxy{*this, index};
    // }

private:
    ws2811_t m_leds;
    int m_count;
    int m_channel;
};
