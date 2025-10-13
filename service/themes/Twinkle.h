#pragma once

#include "Theme.h"
#include "Palette.h"
#include <vector>
#include <memory>

class Twinkle : public Theme
{
public:
    using Theme::Theme;
    ~Twinkle() = default;

    void run() override;

    void setAttribute(const std::string &key, const std::string &value) override;

private:
    void themeInit() override;

    int twinkleSpeed{4};
    int twinkleDensity{6};
    int secondsPerPalette{30};
    uint32_t lastPaletteChangeMs{0};
    uint32_t lastBlendMs{0};
    // bool autoSelectBg;
    bool coolLikeIncandescent{true};

    // Keep the reference palettes as immutable templates; do not modify them.
    std::vector<std::reference_wrapper<const Palette>> palettes;

    // Working palette is a mutable copy that we blend toward a target template.
    std::unique_ptr<Palette> workingPalette;
    Palette *currentPalette = nullptr;      // points to workingPalette.get()
    const Palette *targetPalette = nullptr; // points into `palettes`
};
