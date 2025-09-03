#pragma once

#include "PixelStrip.h"
#include <vector>
#include <cstdint>

class Fire2012 {
    public:
        Fire2012(PixelStrip& pixelStrip);
        ~Fire2012();

        void init();

        void run();

    private:
        PixelStrip& strip;
        int cooling;
        int sparking;
        bool reverseDirection;

        std::vector<uint8_t> heat;
};