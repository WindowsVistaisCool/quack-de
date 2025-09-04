#include "Jerry.h"
#include "PixelStrip.h"
#include "LEDMath8.h"
#include "Color.h"
#include <algorithm>
#include <thread>
#include <chrono>

void Jerry::themeInit()
{
    strip.clear();
    hue = 0;
    tailScaleFactor = 250;
    step_size = 1;
}

void Jerry::run()
{
    int num = strip.numPixels();
    if (num <= 0) return;

    int _step_size = std::max(1, step_size);

    for (int i = 0; i < num; i += _step_size) {
        if (shouldReturn()) return;

        hue = static_cast<uint8_t>(hue + 4);

        // fill pixels for step size
        int fillCount = std::min(_step_size, num - i);
        Color c = Color::fromHSV(hue, 255, 255);
        for (int offset = 0; offset < fillCount; ++offset) {
            int idx = i + offset;
            if (idx < num) {
                strip.setPixelColor(idx, c);
            }
        }

        // tail fading: scale every pixel by tailScaleFactor
        uint8_t scale = static_cast<uint8_t>(std::clamp(tailScaleFactor, 0, 255));
        for (int k = 0; k < num; ++k) {
            if ((k & 31) == 0 && shouldReturn()) return; // periodic quick exit
            Color rgb = strip.getPixelColor(k);
            uint8_t r = scale8(rgb.r, scale);
            uint8_t g = scale8(rgb.g, scale);
            uint8_t b = scale8(rgb.b, scale);
            strip.setPixelColor(k, Color(r, g, b));
        }

        // detect step_size changes and update _step_size; continue with loop
        if (_step_size != std::max(1, step_size)) {
            _step_size = std::max(1, step_size);
            continue;
        }

        strip.show();
        // small sleep to avoid starving CPU (original had 10ms)
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

