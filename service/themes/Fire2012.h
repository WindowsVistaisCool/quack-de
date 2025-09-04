#pragma once

#include "Theme.h"
#include <vector>
#include <cstdint>

class Fire2012 : public Theme
{
public:
    using Theme::Theme;
    ~Fire2012() override;

    void run() override;

private:
    void themeInit() override;
    int cooling;
    int sparking;
    bool reverseDirection;
    std::vector<uint8_t> heat;
};