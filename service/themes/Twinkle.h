#pragma once

#include "Theme.h"
#include "Palette.h"
#include <vector>

class Twinkle : public Theme
{
public:
    using Theme::Theme;
    ~Twinkle() = default;

    void run() override;

private:
    void themeInit() override;

    int twinkleSpeed;
    int twinkleDensity;
    int secondsPerPalette;
    // bool autoSelectBg;
    bool coolLikeIncandescent;

    std::vector<std::reference_wrapper<Palette>> palettes;
    Palette* currentPalette = nullptr;
};
