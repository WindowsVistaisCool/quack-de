#include "Pacifica.h"
#include "PixelStrip.h"

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
    
}