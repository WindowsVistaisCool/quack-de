#include "PixelStrip.h"
#include "Color.h"
#include <cstring>
#include <iostream>
#include "LEDMath8.h"
#include <chrono>
#include <mutex>

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
    std::lock_guard<std::mutex> lk(m_mutex);
    ws2811_return_t rc = ws2811_init(&m_leds);
    if (rc != WS2811_SUCCESS)
    {
        std::cerr << "ws2811_init failed: " << ws2811_get_return_t_str(rc) << std::endl;
        return false;
    }
    return true;
}

void PixelStrip::setBrightness(uint8_t brightness, bool log)
{
    if (log)
    {
        // TODO
        //     uint8_t log_brightness = (uint8_t)(std::pow(2.0, brightness / 32.0) - 1);
        //     brightness = log_brightness;
    }
    std::lock_guard<std::mutex> lk(m_mutex);
    m_leds.channel[m_channel].brightness = brightness;
}

void PixelStrip::setColor(const Color &color)
{
    std::lock_guard<std::mutex> lk(m_mutex);
    for (int i = 0; i < m_count; ++i)
    {
        uint32_t col = ((uint32_t)color.r << 16) | ((uint32_t)color.g << 8) | (uint32_t)color.b;
        m_leds.channel[m_channel].leds[i] = col;
    }
    // render while holding mutex to avoid concurrent modification
    ws2811_render(&m_leds);
    ws2811_wait(&m_leds);
}

void PixelStrip::show()
{
    std::lock_guard<std::mutex> lk(m_mutex);
    // Log render start time to help correlate flashes with render calls
    auto now = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    std::cout << "[PixelStrip] render start: " << ms << " ms" << std::endl;

    ws2811_render(&m_leds);

    // Wait for the DMA/render to complete before returning to avoid buffer modifications
    // while a transfer is in progress. This helps rule out mid-transfer corruption.
    ws2811_wait(&m_leds);

    auto done = std::chrono::steady_clock::now();
    auto done_ms = std::chrono::duration_cast<std::chrono::milliseconds>(done.time_since_epoch()).count();
    std::cout << "[PixelStrip] render end: " << done_ms << " ms (dur=" << (done_ms - ms) << " ms)" << std::endl;
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
    std::lock_guard<std::mutex> lk(m_mutex);
    m_leds.channel[m_channel].leds[index] = color;
}

uint32_t PixelStrip::getRawPixelColor(int index)
{
    if (index < 0 || index >= m_count)
        return 0;
    std::lock_guard<std::mutex> lk(m_mutex);
    return m_leds.channel[m_channel].leds[index];
}

Color PixelStrip::getPixelColor(int index)
{
    uint32_t color = getRawPixelColor(index);
    return Color{(uint8_t)((color >> 16) & 0xFF), (uint8_t)((color >> 8) & 0xFF), (uint8_t)(color & 0xFF)};
}

uint8_t PixelStrip::getPixelAverageLight(int index)
{
    Color c = getPixelColor(index);
    uint8_t avg = scale8(c.r, 85) +
                  scale8(c.g, 85) +
                  scale8(c.b, 85);
    return avg;
}

void PixelStrip::clear()
{
    std::lock_guard<std::mutex> lk(m_mutex);
    for (int i = 0; i < m_count; ++i)
        m_leds.channel[m_channel].leds[i] = 0;
    ws2811_render(&m_leds);
    ws2811_wait(&m_leds);
}
