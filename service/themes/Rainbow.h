#pragma once

#include "Theme.h"

class Rainbow : public Theme {
public:
    using Theme::Theme;
    ~Rainbow() = default;

    void run() override;

    void setAttribute(const std::string &key, const std::string &value) override;
    
private:
    void themeInit() override;

    int iterations;
    int delay;
    int step_size;
};