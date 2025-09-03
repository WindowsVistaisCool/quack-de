#include "Pacifica.h"
#include "Palette.h"
#include "PixelStrip.h"
#include "LEDMath8.h"
#include <thread>

Pacifica::Pacifica(PixelStrip &pixelStrip) : Theme(pixelStrip)
{
    init();
}

void Pacifica::init()
{
    strip.clear();
}

void Pacifica::run()
{
    // Increment the four "color index start" counters, one for each wave layer.
    // Each is incremented at a different speed, and the speeds vary over time.
    static uint16_t sCIStart1, sCIStart2, sCIStart3, sCIStart4;
    static uint32_t sLastms = 0;

    uint32_t ms = GET_MILLIS();
    uint32_t deltams = ms - sLastms;
    sLastms = ms;
    uint16_t speedfactor1 = beatsin16(3, 179, 269);
    uint16_t speedfactor2 = beatsin16(4, 179, 269);
    uint32_t deltams1 = (deltams * speedfactor1) / 256;
    uint32_t deltams2 = (deltams * speedfactor2) / 256;
    uint32_t deltams21 = (deltams1 + deltams2) / 2;
    sCIStart1 += (deltams1 * beatsin88(1011, 10, 13));
    sCIStart2 -= (deltams21 * beatsin88(777, 8, 11));
    sCIStart3 -= (deltams1 * beatsin88(501, 5, 7));
    sCIStart4 -= (deltams2 * beatsin88(257, 4, 6));

    // Clear out the LED array to a dim background blue-green
    for (int i = 0; i < strip.numPixels(); i++)
    {
        strip.setPixelColor(i, Color{2, 6, 10});
    }

    // Render each of four layers, with different scales and speeds, that vary over time
    waves_one_layer(pacifica1, sCIStart1, beatsin16(3, 11 * 256, 14 * 256), beatsin8(10, 70, 130), 0 - beat16(301));
    waves_one_layer(pacifica2, sCIStart2, beatsin16(4, 6 * 256, 9 * 256), beatsin8(17, 40, 80), beat16(401));
    waves_one_layer(pacifica3, sCIStart3, 6 * 256, beatsin8(9, 10, 38), 0 - beat16(503));
    waves_one_layer(pacifica3, sCIStart4, 5 * 256, beatsin8(8, 10, 28), beat16(601));

    // Add brighter 'whitecaps' where the waves lines up more
    waves_add_whitecaps();

    // Deepen the blues and greens a bit
    waves_deepen_colors();

    strip.show();
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
}

void Pacifica::waves_one_layer(Palette& p, uint16_t cistart, uint16_t wavescale, uint8_t bri, uint16_t ioff)
{
    uint16_t ci = cistart;
    uint16_t waveangle = ioff;
    uint16_t wavescale_half = (wavescale / 2) + 20;
    for( uint16_t i = 0; i < strip.numPixels(); i++) {
        waveangle += 250;
        uint16_t s16 = sin16( waveangle ) + 32768;
        uint16_t cs = scale16( s16 , wavescale_half ) + wavescale_half;
        ci += cs;
        uint16_t sindex16 = sin16( ci) + 32768;
        uint8_t sindex8 = scale16( sindex16, 240);
        Color c = ColorFromPalette( p, sindex8, bri, LINEARBLEND);
        strip.setPixelColor(i, strip.getPixelColor(i) + c);
    }
}

void Pacifica::waves_add_whitecaps()
{
    uint8_t basethreshold = beatsin8(9, 55, 65);
    uint8_t wave = beat8(7);

    for (uint16_t i = 0; i < strip.numPixels(); i++)
    {
        uint8_t threshold = scale8(sin8(wave), 20) + basethreshold;
        wave += 7;
        uint8_t l = strip.getPixelAverageLight(i);
        if (l > threshold)
        {
            uint8_t overage = l - threshold;
            uint8_t overage2 = qadd8(overage, overage);
            strip.setPixelColor(i, strip.getPixelColor(i) + Color{overage, overage2, qadd8(overage2, overage2)});
        }
    }
}

void Pacifica::waves_deepen_colors()
{
    for (uint16_t i = 0; i < strip.numPixels(); i++)
    {
        Color c = strip.getPixelColor(i);
        c.g = scale8(c.g, 224);
        c.b = scale8(c.b, 255);
        c |= Color{2, 5, 7};
        strip.setPixelColor(i, c);
    }
}
