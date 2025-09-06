#pragma once

#include "Theme.h"

class Rainbow : public Theme {
public:
    using Theme::Theme;
    ~Rainbow() = default;

    void run() override;
    
private:
    void themeInit() override;

    int iterations;
    int delay;
    int step_size;
};