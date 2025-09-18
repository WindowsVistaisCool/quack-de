#pragma once

#include "Theme.h"

class Epilepsy : public Theme
{
public:
    using Theme::Theme;
    ~Epilepsy() = default;

    void run() override;

private:
    void themeInit() override;
};