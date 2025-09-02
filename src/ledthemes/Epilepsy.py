import colorsys
from time import time
# from LEDThemes import FastLEDFunctions
from lib.led.LEDTheme import LEDTheme, MPCTargetParams

def fromHSV(hue, sat, val):
    rgb = colorsys.hsv_to_rgb(hue / 255.0, sat / 255.0, val / 255.0)
    return (
        int(rgb[0] * 255) & 0xFF,
        int(rgb[1] * 255) & 0xFF,
        int(rgb[2] * 255) & 0xFF,
    )

def target(theme: "MPCTargetParams"):
    # nonlocal hue
    hue = 0
    hue = (hue + 32) & 0xFF

    for i in range(theme.strip.numPixels()):
        theme.strip.setPixelColorRGB(i, *fromHSV(hue, 255, 255))
    theme.strip.show()

    time.sleep(0.05)

    for i in range(theme.strip.numPixels()):
        theme.strip.setPixelColorRGB(i, 0, 0, 0)
    theme.strip.show()

    time.sleep(0.05)

def get():
    # num = ctk.IntVar(value=0)
    hue = 0

    return LEDTheme(
        "epilepsy",
        target,
        allowMPC=True
    )