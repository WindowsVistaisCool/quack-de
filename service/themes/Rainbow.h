#pragma once

#include "Theme.h"

class Rainbow : public Theme {
public:
    Rainbow(PixelStrip &pixelStrip);
    ~Rainbow() = default;

    void init() override;
    void run() override;

private:
    int iterations;
    int delay;
    int step_size;
};