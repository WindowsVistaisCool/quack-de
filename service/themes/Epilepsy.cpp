#include "Epilepsy.h"
#include "PixelStrip.h"
#include "Color.h"
#include <thread>
#include <chrono>

void Epilepsy::themeInit()
{

}

void Epilepsy::run()
{
    static int hue = 0;

    hue = (hue + 32) & 0xFF;

    for (int i = 0; i < strip.numPixels(); i++) {
        strip.setPixelColor(i, Color::fromHSV(hue, 255, 255));
    }
    strip.show();

    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    for (int i = 0; i < strip.numPixels(); i++) {
        strip.setPixelColor(i, 0, 0, 0);
    }
    strip.show();

    std::this_thread::sleep_for(std::chrono::milliseconds(50));

}
