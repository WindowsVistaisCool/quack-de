#include "Twinkle.h"
#include "PixelStrip.h"
#include <thread>
#include <chrono>

void Twinkle::themeInit()
{
    strip.clear();
    twinkleSpeed = 5;
    twinkleDensity = 2;
    secondsPerPalette = 30;
    coolLikeIncandescent = true;

    palettes.clear();
    static Palette retroC9({
        Color(0xB80400), // C9_Red
        Color(0x902C02), // C9_Orange
        Color(0xB80400), // C9_Red
        Color(0x902C02), // C9_Orange
        Color(0x902C02), // C9_Orange
        Color(0xB80400), // C9_Red
        Color(0x902C02), // C9_Orange
        Color(0xB80400), // C9_Red
        Color(0x046002), // C9_Green
        Color(0x046002), // C9_Green
        Color(0x046002), // C9_Green
        Color(0x046002), // C9_Green
        Color(0x070758), // C9_Blue
        Color(0x070758), // C9_Blue
        Color(0x070758), // C9_Blue
        Color(0x606820)  // C9_White
    });
    palettes.push_back(std::ref(retroC9));
    currentPalette = &palettes[0].get();
}

void Twinkle::run()
{
    // do palette switching here

    // do blend here

    uint16_t PRNG16 = 11337;

    uint32_t clock32 = GET_MILLIS();

    // Set up the background color, "bg".
    // if AUTO_SELECT_BACKGROUND_COLOR == 1, and the first two colors of
    // the current palette are identical, then a deeply faded version of
    // that color is used for the background color
    Color bg;
    if (0 == 1)
    {
        // bg = gCurrentPalette[0];
        // uint8_t bglight = bg.getAverageLight();
        // if (bglight > 64)
        // {
        //     bg.nscale8_video(16); // very bright, so scale to 1/16th
        // }
        // else if (bglight > 16)
        // {
        //     bg.nscale8_video(64); // not that bright, so scale to 1/4th
        // }
        // else
        // {
        //     bg.nscale8_video(86); // dim, scale to 1/3rd.
        // }
    }
    else
    {
        bg = Color(0); // Color(Color::FairyLight).nscale8_video(16);// just use the explicitly defined background color
    }

    const uint8_t backgroundBrightness = 0;

    for (uint16_t i = 0; i < strip.numPixels(); i++)
    {
        // advance PRNG and produce a per-pixel offset; mix in pixel index
        PRNG16 = (uint16_t)(PRNG16 * 2053) + 1384;              // next 'random' number
        uint16_t myclockoffset16 = PRNG16 ^ (uint16_t)(i * 73); // mix in index to de-cluster
        PRNG16 = (uint16_t)(PRNG16 * 2053) + 1384;              // next 'random' number
        // use that number as clock speed adjustment factor (in 8ths, from 8/8ths to 23/8ths)
        uint8_t myspeedmultiplierQ5_3 = ((((PRNG16 & 0xFF) >> 4) + (PRNG16 & 0x0F)) & 0x0F) + 0x08;
        uint32_t myclock30 = (uint32_t)((clock32 * myspeedmultiplierQ5_3) >> 3) + myclockoffset16;
        uint8_t myunique8 = PRNG16 >> 8; // get 'salt' value for this pixel

        // We now have the adjusted 'clock' for this pixel, now we call
        // the function that computes what color the pixel should be based
        // on the "brightness = f( time )" idea.
        uint32_t ms = myclock30;
        uint8_t salt = myunique8;

        uint16_t ticks = ms >> (8 - twinkleSpeed);
        uint8_t fastcycle8 = ticks;
        uint16_t slowcycle16 = (ticks >> 8) + salt;
        slowcycle16 += sin8(slowcycle16);
        slowcycle16 = (slowcycle16 * 2053) + 1384;
        uint8_t slowcycle8 = (slowcycle16 & 0xFF) + (slowcycle16 >> 8);

        uint8_t bright = 0;
        if (((slowcycle8 & 0x0E) / 2) < twinkleDensity)
        {
            uint8_t j = fastcycle8;
            if (j < 86)
            {
                bright = j * 3;
            }
            else
            {
                j -= 86;
                // reduce the influence of the pixel index to avoid spatial
                // bands of choppiness; compute with signed arithmetic and clamp
                // to avoid underflow/wrap when (j + (i>>3)) > 255.
                {
                    int sum = static_cast<int>(j) + static_cast<int>(i >> 3);
                    int val = 255 - sum;
                    if (val < 0)
                        val = 0;
                    if (val > 255)
                        val = 255;
                    bright = static_cast<uint8_t>(val);
                }
            }
        }

        uint8_t hue = slowcycle8 - salt;
        Color c;
        if (bright > 0)
        {
            c = ColorFromPalette(*currentPalette, hue, bright, NOBLEND);
            if (coolLikeIncandescent == 1)
            {
                if (fastcycle8 >= 128)
                {
                    uint8_t cooling = (fastcycle8 - 128) >> 4;
                    c.g = qsub8(c.g, cooling);
                    c.b = qsub8(c.b, cooling * 2);
                }
            }
        }
        else
        {
            c = Color(0);
        }

        uint8_t cbright = c.getAverageLight();
        int16_t deltabright = cbright - backgroundBrightness;
        if (deltabright >= 32)
        {
            // If the new pixel is significantly brighter than the background color,
            // use the new color.
            strip.setPixelColor(i, c);
        }
        else if (deltabright > 0)
        {
            // If the new pixel is just slightly brighter than the background color,
            // mix a blend of the new color and the background color
            strip.setPixelColor(i, blend(bg, c, deltabright * 8));
        }
        else
        {
            // if the new pixel is not at all brighter than the background color,
            // just use the background color.
            strip.setPixelColor(i, bg);
        }
    }
    if (shouldReturn())
    {
        return;
    }
    else
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    strip.show();
}
