#pragma once

#include "Theme.h"

class Pacifica : public Theme {
public:
    Pacifica(PixelStrip &pixelStrip);
    ~Pacifica() = default;

    void init() override;
    void run() override;
private:
    int stuff = 0;
};