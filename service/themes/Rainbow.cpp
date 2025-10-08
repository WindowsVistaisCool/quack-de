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

void Rainbow::themeInit()
{
    iterations = 90;
    step_size = 14;
    delay = 20;
}

void Rainbow::run()
{
    for (int i = 0; i < 256; i += step_size)
    {
        // quick-exit check before starting this pass
        if (shouldReturn()) {
            return;
        }
        for (int j = 0; j < strip.numPixels(); ++j)
        {
            // check periodically inside the inner loop so we don't wait
            // for the whole pass to finish before exiting
            if ((j & 15) == 0 && shouldReturn()) {
                return;
            }
            int hue = ((j * 256 / iterations) + i) & 255;
            Color color = rainbowWheel(hue);
            strip.setPixelColor(j, color);
        }
        strip.show();

        if (delay > 0)
        {
            if (shouldReturn())
            {
                return;
            }
            // std::this_thread::sleep_for(std::chrono::milliseconds(delay));
        }
    }
}

void Rainbow::setAttribute(const std::string &key, const std::string &value)
{
    if (key == "iterations")
    {
        int val = std::stoi(value);
        if (val > 0)
        {
            iterations = val;
        }
    }
    else if (key == "step_size")
    {
        int val = std::stoi(value);
        if (val > 0)
        {
            step_size = val;
        }
    }
    else if (key == "delay")
    {
        int val = std::stoi(value);
        if (val >= 0)
        {
            delay = val;
        }
    }
}
