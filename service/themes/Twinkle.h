#pragma once

#include "Theme.h"

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
};
