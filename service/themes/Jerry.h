#pragma once

#include "Theme.h"

class Jerry : public Theme {
public:
    using Theme::Theme;
    ~Jerry() = default;

    void run() override;

private:
    void themeInit() override;

    uint8_t hue;
    int tailScaleFactor;
    int step_size;
};
