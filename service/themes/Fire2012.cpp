#include "Fire2012.h"
#include "PixelStrip.h"
#include "Color.h"
#include "LEDMath8.h"

Fire2012::~Fire2012()
{
    heat.clear();
}

void Fire2012::themeInit()
{
    strip.clear();

    cooling = 65;
    sparking = 130;
    reverseDirection = false;

    // Ensure the heat buffer matches the number of pixels
    heat.clear();
    heat.resize(strip.numPixels(), 0);
}

void Fire2012::run()
{
    for (int i = 0; i < strip.numPixels(); i++)
    {
        heat[i] = qsub8(heat[i], random8(0, ((cooling * 10) / strip.numPixels()) + 2));
    }

    // Step 2.  Heat from each cell drifts 'up' and diffuses a little
    for (int k = strip.numPixels() - 1; k >= 2; k--)
    {
        heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3;
    }

    // Step 3.  Randomly ignite new 'sparks' of heat near the bottom
    if (random8(0, 255) < sparking)
    {
        int y = random8(7);
        heat[y] = qadd8(heat[y], random8(160, 255));
    }

    // Step 4.  Map from heat cells to LED colors
    for (int j = 0; j < strip.numPixels(); j++)
    {
        Color color = HeatColor(heat[j]);
        int pixelnumber;
        if (reverseDirection)
        {
            pixelnumber = (strip.numPixels() - 1) - j;
        }
        else
        {
            pixelnumber = j;
        }
        strip.setPixelColor(pixelnumber, color);
    }

    strip.show();
}

void Fire2012::setAttribute(const std::string &key, const std::string &value)
{
    if (key == "cooling") {
        int val = std::stoi(value);
        cooling = std::clamp(val, 20, 200); // Valid range: 20-200
    } else if (key == "sparking") {
        int val = std::stoi(value);
        sparking = std::clamp(val, 50, 250); // Valid range: 50-250
    } else if (key == "reverseDirection") {
        if (value == "true" || value == "1") {
            reverseDirection = true;
        } else if (value == "false" || value == "0") {
            reverseDirection = false;
        }
    }
}
