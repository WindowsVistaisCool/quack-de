#include "Rainbow.h"
#include "PixelStrip.h"
#include <thread>

Color rainbowWheel(uint8_t pos)
{
    if (pos < 85)
    {
        return Color{static_cast<uint8_t>(pos * 3), static_cast<uint8_t>(255 - pos * 3), static_cast<uint8_t>(0)};
    }
    else if (pos < 170)
    {
        pos -= 85;
        return Color{static_cast<uint8_t>(255 - pos * 3), static_cast<uint8_t>(0), static_cast<uint8_t>(pos * 3)};
    }
    else
    {
        pos -= 170;
        return Color{static_cast<uint8_t>(0), static_cast<uint8_t>(pos * 3), static_cast<uint8_t>(255 - pos * 3)};
    }
}

Rainbow::Rainbow(PixelStrip &pixelStrip) : Theme(pixelStrip)
{
    init();
}

void Rainbow::init()
{
    iterations = 90;
    step_size = 14;
    delay = 20;
}

void Rainbow::run()
{
    for (int i = 0; i < 256; i += step_size)
    {
        for (int j = 0; j < strip.numPixels(); ++j)
        {
            int hue = ((j * 256 / iterations) + i) & 255;
            Color color = rainbowWheel(hue);
            strip.setPixelColor(j, color);
        }
        strip.show();
    
        if (delay > 0)
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(delay));
        }
    }
}