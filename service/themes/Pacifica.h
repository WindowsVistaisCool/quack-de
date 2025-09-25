#pragma once

#include "Theme.h"
#include "Palette.h"
#include "Color.h"

#define DEFAULT_SHIFT_DELAY 10
#define DEFAULT_LOWER_BOUND -30
#define DEFAULT_UPPER_BOUND 35

class Pacifica : public Theme
{
public:
    Pacifica(PixelStrip &strip, int shiftDelay, int lowShiftBound, int highShiftBound);
    Pacifica(PixelStrip &strip) : Pacifica(strip, DEFAULT_SHIFT_DELAY, DEFAULT_LOWER_BOUND, DEFAULT_UPPER_BOUND) {}
    ~Pacifica() = default;

    void run() override;

private:
    void themeInit() override;

    int shiftDelay {};
    int lowShiftBound {};
    int highShiftBound {};

    void waves_one_layer(const Palette &p, uint16_t cistart, uint16_t wavescale, uint8_t bri, uint16_t ioff);
    void waves_add_whitecaps();
    void waves_deepen_colors();

    void hueShift(int hueAdd);

    const Palette pacifica1 = Palette({Color(0x000507),
                                       Color(0x000409),
                                       Color(0x00030B),
                                       Color(0x00030D),
                                       Color(0x000210),
                                       Color(0x000212),
                                       Color(0x000114),
                                       Color(0x000117),
                                       Color(0x000019),
                                       Color(0x00001C),
                                       Color(0x000026),
                                       Color(0x000031),
                                       Color(0x00003B),
                                       Color(0x000046),
                                       Color(0x14554B),
                                       Color(0x28AA50)});
   const Palette pacifica2 = Palette({Color(0x000507),
                                       Color(0x000409),
                                       Color(0x00030B),
                                       Color(0x00030D),
                                       Color(0x000210),
                                       Color(0x000212),
                                       Color(0x000114),
                                       Color(0x000117),
                                       Color(0x000019),
                                       Color(0x00001C),
                                       Color(0x000026),
                                       Color(0x000031),
                                       Color(0x00003B),
                                       Color(0x000046),
                                       Color(0x0C5F52),
                                       Color(0x19BE5F)});
    const Palette pacifica3 = Palette({Color(0x000208),
                                       Color(0x00030E),
                                       Color(0x000514),
                                       Color(0x00061A),
                                       Color(0x000820),
                                       Color(0x000927),
                                       Color(0x000B2D),
                                       Color(0x000C33),
                                       Color(0x000E39),
                                       Color(0x001040),
                                       Color(0x001450),
                                       Color(0x001860),
                                       Color(0x001C70),
                                       Color(0x002080),
                                       Color(0x1040BF),
                                       Color(0x2060FF)});
};