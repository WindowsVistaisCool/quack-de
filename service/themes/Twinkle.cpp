#include "Twinkle.h"
#include "PixelStrip.h"

void Twinkle::themeInit()
{
    strip.clear();
    twinkleSpeed = 3;
    twinkleDensity = 4;
    secondsPerPalette = 30;
    coolLikeIncandescent = true;
}

void Twinkle::run()
{
    strip.setColor(Color(255, 0, 0));
    
}
