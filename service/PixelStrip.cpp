#include "PixelStrip.h"
#include <cstring>
#include <iostream>

PixelStrip::PixelStrip(int count, int gpio, int dma, int freq, int channel)
    : m_count(count), m_channel(channel)
{
    memset(&m_leds, 0, sizeof(ws2811_t));

    m_leds.freq = freq;
    m_leds.dmanum = dma;
    m_leds.channel[channel].gpionum = gpio;
    m_leds.channel[channel].count = count;
    m_leds.channel[channel].invert = 0;
    m_leds.channel[channel].brightness = 255;
    m_leds.channel[channel].strip_type = WS2812_STRIP;
}

PixelStrip::~PixelStrip()
{
    ws2811_fini(&m_leds);
}

bool PixelStrip::begin()
{
    ws2811_return_t rc = ws2811_init(&m_leds);
    if (rc != WS2811_SUCCESS)
    {
        std::cerr << "ws2811_init failed: " << ws2811_get_return_t_str(rc) << std::endl;
        return false;
    }
    return true;
}

void PixelStrip::setBrightness(uint8_t brightness)
{
    m_leds.channel[m_channel].brightness = brightness;
}

void PixelStrip::show()
{
    ws2811_render(&m_leds);
}

void PixelStrip::setPixelColor(int index, const Color &color)
{
    setPixelColor(index, color.r, color.g, color.b);
}

void PixelStrip::setPixelColor(int index, uint8_t r, uint8_t g, uint8_t b)
{
    if (index < 0 || index >= m_count)
        return;
    uint32_t color = ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
    m_leds.channel[m_channel].leds[index] = color;
}

uint32_t PixelStrip::getRawPixelColor(int index)
{
    if (index < 0 || index >= m_count)
        return -1;
    return m_leds.channel[m_channel].leds[index];
}

Color PixelStrip::getPixelColor(int index)
{
    uint32_t color = getRawPixelColor(index);
    return Color{(uint8_t)((color >> 16) & 0xFF), (uint8_t)((color >> 8) & 0xFF), (uint8_t)(color & 0xFF)};
}

void PixelStrip::clear()
{
    for (int i = 0; i < m_count; ++i)
        m_leds.channel[m_channel].leds[i] = 0;
    show();
}
