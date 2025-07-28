import math
import rpi_ws281x as ws
import threading
import time

class FastLEDFunctions:
    """
    Contains various functions ported from FastLED library for LED control.

    Ported by Kyle Rush
    """

    @staticmethod
    def nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges=24):
        """Blend currentPalette toward targetPalette."""
        currentPalette = list(currentPalette)
        changes = 0
        numColors = min(len(currentPalette), len(targetPalette))
        for i in range(numColors):
            if changes >= maxChanges:
                break
            currentColor = currentPalette[i]
            targetColor = targetPalette[i]
            if currentColor != targetColor:
                if (currentColor < targetColor):
                    currentPalette[i] += 1
                    changes += 1
                elif (currentColor > targetColor):
                    currentPalette[i] -= 1
                    changes += 1
                    if currentColor > targetColor:
                        currentPalette[i] -= 1    
        return tuple(currentPalette)

    @classmethod
    def getAverageLight(cls, crgb):
        eightyFive = 85 # dont ask
        return cls.scale8(crgb[0], eightyFive) + cls.scale8(crgb[1], eightyFive) + cls.scale8(crgb[2], eightyFive)

    @staticmethod
    def scale8(value, scale):
        return ((int(value) & 0xFFFF) * ((int(scale) & 0xFFFF) + 1)) >> 8

    @classmethod
    def ColorFromPalette(cls, palette: tuple, index: int, brightness: int = 255, _: str = "NOBLEND"):
        if not palette:
            return (0, 0, 0)
        
        # Extract the high 4 bits to get palette index (equivalent to index >> 4)
        hi4 = index >> 4
        # Clamp hi4 to valid palette range
        palette_index = hi4 % len(palette)
        
        # Get the color from the palette
        color = palette[palette_index]
        # convert color from hex to rgb components
        if isinstance(color, int):
            color = ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)

        red1, green1, blue1 = int(color[0]), int(color[1]), int(color[2])
        
        # Apply brightness scaling if not full brightness
        if brightness != 255:
            if brightness > 0:
                # Adjust for rounding like the C++ version
                brightness += 1
                if brightness > 255:
                    brightness = 255
                
                # Scale each component and add 1 if non-zero (FastLED behavior)
                if red1:
                    red1 = cls.scale8(red1, brightness)
                    red1 += 1
                    if red1 > 255:
                        red1 = 255
                
                if green1:
                    green1 = cls.scale8(green1, brightness)
                    green1 += 1
                    if green1 > 255:
                        green1 = 255
                
                if blue1:
                    blue1 = cls.scale8(blue1, brightness)
                    blue1 += 1
                    if blue1 > 255:
                        blue1 = 255
            else:
                # Zero brightness means black
                red1 = green1 = blue1 = 0
        return (red1, green1, blue1)
    
    @staticmethod
    def blend8(a, b, amountB):
        partial = (a << 8) | b

        partial += (b * amountB)
        partial -= (a *  amountB)

        return (partial >> 8) & 0xFF
    
    @staticmethod
    def blend(c1, c2, amountC2):
        """Blend two colors c1 and c2 by amountC2 (0-255)."""
        r = FastLEDFunctions.blend8(c1[0], c2[0], amountC2)
        g = FastLEDFunctions.blend8(c1[1], c2[1], amountC2)
        b = FastLEDFunctions.blend8(c1[2], c2[2], amountC2)
        return (r, g, b)

    @staticmethod
    def _wheel(pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return ws.Color(pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return ws.Color(255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return ws.Color(0, pos * 3, 255 - pos * 3)

class LEDLoops:
    @staticmethod
    def null():
        return lambda *_ : True

    @staticmethod
    def rainbow(iterations=1):
        iterations = int(iterations)
        def target(leds: 'ws.PixelStrip', break_event: 'threading.Event'):
            for j in range(256 * iterations):
                if break_event.is_set():
                    return True
                for i in range(leds.numPixels()):
                    leds.setPixelColor(i, FastLEDFunctions._wheel(((i * 256 // iterations) + j) & 255))
                leds.show()
                time.sleep(20 / 1000.0)  # 20 ms delay
        return target
    
    @staticmethod
    def holidayTwinkle(afterCallable = lambda _, _0: None):
        """
        This function creates a twinkle effect for holiday lights.
        Originally wrote for Arduino but adapted for Python.
        """

        class Palette:
            def __init__(self, name, colors, palette=None):
                self.name = name
                self.colors = colors
                self.palette = []
                
                if palette:
                    self.palette = [self.colors[i] for i in palette]
            
            def get(self):
                return tuple(self.palette)

        palettes = (
            Palette(
                "C9",
                {
                    'red': 0xbb80400,
                    'orange': 0x902c02,
                    'green': 0x046002,
                    'blue': 0x070758,
                    'white': 0x606820,
                },
                [
                    'red', 'orange', 'red', 'orange',
                    'orange', 'red', 'orange', 'red',
                    'green', 'green', 'green', 'green',
                    'blue', 'blue', 'blue', 'white'
                ]
            ),
            Palette(
                "Blue and White",
                {'blue': 0x00000FF, 'gray': 0x808080},
                [
                    'blue', 'blue', 'blue', 'blue',
                    'blue', 'blue', 'blue', 'blue',
                    'blue', 'blue', 'blue', 'blue',
                    'blue', 'gray', 'gray', 'gray'
                ]
            ),
            # Palette(
            #     "Rainbow Colors",
            #     {'pholder': 0x000000},
            #     ['pholder']
            # ),
            Palette(
                "Fairy Lights",
                {
                    'fairy': 0xFFE42D,
                    'half-fairy': int((0xFFE42D & 0xFEFEFE) / 2) & 0xFFFFFF,
                    'quarter-fairy': int((0xFFE42D & 0xFCFCFC) / 4) & 0xFFFFFF,
                },
                [
                    'fairy', 'fairy', 'fairy', 'fairy',
                    'half-fairy', 'half-fairy', 'fairy', 'fairy',
                    'quarter-fairy', 'quarter-fairy', 'fairy', 'fairy',
                    'fairy', 'fairy', 'fairy', 'fairy'
                ]
            )
        )

        twinkleSpeed = 4 # 1-8
        twinkleDensity = 5 # 1-8
        secondsPerPallette = 10 # seconds
        autoSelectBackgroundColor = False
        coolLikeIncandescent = True

        rawPalettes = [p.get() for p in palettes]
        currentIndex = 0
        targetPalette = rawPalettes[currentIndex]
        currentPalette = targetPalette

        ms_0 = int(time.time() * 1000)

        blendCallRunning = False
        paletteSwapCallRunning = False
        def target(leds: 'ws.PixelStrip', break_event: 'threading.Event'):
            nonlocal blendCallRunning, paletteSwapCallRunning, currentPalette, targetPalette, ms_0

            def swap_palette():
                if break_event.is_set():
                    return
                nonlocal currentIndex, targetPalette
                currentIndex = (currentIndex + 1) % len(rawPalettes)
                targetPalette = rawPalettes[currentIndex]
                afterCallable(1000 * secondsPerPallette, swap_palette)

            def blend_target():
                if break_event.is_set():
                    return
                nonlocal currentPalette, targetPalette
                currentPalette = targetPalette
                # currentPalette = FastLEDFunctions.nblendPaletteTowardPalette(currentPalette, targetPalette, 12)
                afterCallable(10, blend_target)

            if not blendCallRunning:
                blend_target()
                blendCallRunning = True
            if not paletteSwapCallRunning:
                afterCallable(1000 * secondsPerPallette, swap_palette)
                paletteSwapCallRunning = True

            rng_16b = 11337
            clock_32b = (int)(time.time() * 1000) - ms_0

            bg = None
            if (autoSelectBackgroundColor):
                pass # TODO: implement?
            else:
                bg = (0, 0, 0)

            bgBrightness_8b = FastLEDFunctions.getAverageLight(bg) & 0xFF

            for i in range(leds.numPixels()):
                if break_event.is_set():
                    leds.show()
                    return True
                
                rng_16b = (rng_16b * 2053) + 1384
                rng_16b &= 0xFFFF  # Ensure PRNG16 is 16 bits
                clockOffset_16b = rng_16b & 0xFFFF
                rng_16b = (rng_16b * 2053) + 1384
                rng_16b &= 0xFFFF  # Ensure PRNG16 is 16 bits

                # use that number as clock speed adjustment factor (in 8ths, from 8/8ths, to 23/8ths)
                speedMultiplier_8b = (((((rng_16b & 0xFF) >> 4) + (rng_16b & 0x0F)) & 0x0F) + 0x08) & 0xFF
                clock30_32b = (((clock_32b * speedMultiplier_8b) >> 3) + clockOffset_16b) & 0xFFFFFFFF # 32 bit
                unique_8b = (rng_16b >> 8) & 0xFF # salt for pixel

                ms_32b = clock30_32b & 0xFFFFFFFF
                salt = unique_8b

                ticks_16b = (ms_32b >> (8 - twinkleSpeed)) & 0xFFFF
                fastCycle_8b = ticks_16b & 0xFF
                slowCycle_16b = ((ticks_16b >> 8) + salt) & 0xFFFF

                slowCycle_16b += int(math.sin(slowCycle_16b) * 255) + 128
                slowCycle_16b &= 0xFFFF
                slowCycle_8b = ((slowCycle_16b & 0xFF) + (slowCycle_16b >> 8)) & 0xFF

                bright_8b = 0
                if (slowCycle_8b & 0x0E) / 2 < twinkleDensity:
                    copy = fastCycle_8b
                    if ( copy < 86 ):
                        bright_8b = copy * 3
                    else:
                        copy -= 86
                        bright_8b = 255 - (copy + int(i / 2))
                    bright_8b &= 0xFF
                
                hue_8b = (slowCycle_8b - salt) & 0xFF
                outputColor = (0, 0, 0)
                if bright_8b > 0:
                    outputColor = FastLEDFunctions.ColorFromPalette(currentPalette, hue_8b, bright_8b)
                    if coolLikeIncandescent:
                        if fastCycle_8b >= 128:
                            cooling = ((fastCycle_8b - 128) >> 4) & 0xFF
                            g = max(outputColor[1] - cooling, 0)
                            b = max(outputColor[2] - (cooling * 2), 0)
                            outputColor = (outputColor[0], g, b)

                outputBrightAvg_8b = FastLEDFunctions.getAverageLight(outputColor) & 0xFF
                deltaBright_8b = (outputBrightAvg_8b - bgBrightness_8b) & 0xFF
                if deltaBright_8b >= 32 or not bg:
                    leds.setPixelColor(i, ws.Color(*outputColor))
                elif deltaBright_8b > 0:
                    leds.setPixelColor(i, ws.Color(*FastLEDFunctions.blend(bg, outputColor, deltaBright_8b * 8)))
                else:
                    leds.setPixelColor(i, ws.Color(*bg))
            leds.show()
    
        return target