#include <iostream>
#include <thread>
#include <chrono>
#include "PixelStrip.h"
#include "themes/Theme.h"
#include "themes/Rainbow.h"

#define LED_COUNT 822
#define LED_PIN 18
#define LED_DMA 10

int main() {
    PixelStrip strip(LED_COUNT, LED_PIN, LED_DMA);
    if (!strip.begin()) {
        std::cerr << "Failed to initialize PixelStrip" << std::endl;
        return 1;
    }

    strip.setBrightness(50);

    // Rainbow theme(strip);

    // while (true) {
    //     theme.run();
    //     // std::this_thread::sleep_for(std::chrono::milliseconds(10));
    // }

    

    return 0;
}
