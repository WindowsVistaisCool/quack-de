#pragma once

#include "Theme.h"
#include <vector>
#include <cstdint>

class Fire2012 : public Theme {
    public:
        Fire2012(PixelStrip& pixelStrip);
        ~Fire2012() override;

        void init() override;

        void run() override;

    private:
        int cooling;
        int sparking;
        bool reverseDirection;
        std::vector<uint8_t> heat;
};