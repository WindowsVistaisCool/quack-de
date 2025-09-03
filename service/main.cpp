#include <iostream>
#include <thread>
#include <chrono>
#include "PixelStrip.h"
#include "themes/Pacifica.h"
#include "LEDMath8.h"

#define LED_COUNT 822
#define LED_PIN 18
#define LED_DMA 10

int main() {
    PixelStrip strip(LED_COUNT, LED_PIN, LED_DMA);
    if (!strip.begin()) {
        std::cerr << "Failed to initialize PixelStrip" << std::endl;
        return 1;
    }

    // strip.setBrightness(40);

    Pacifica theme(strip);

    while (true) {
        theme.run();
    }

    return 0;
}
