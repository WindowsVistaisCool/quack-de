import customtkinter as ctk
import colorsys
import math
import random
import rpi_ws281x as ws
import time

from lib.CommandUI import CommandUI
from lib.SwappableUI import SwappableUI
from lib.led.LEDTheme import LEDTheme


class FastLEDFunctions:
    """
    Contains various functions ported from FastLED library for LED control.

    Ported by Kyle Rush
    """

    @staticmethod
    def fromHSV(hue, sat, val):
        rgb = colorsys.hsv_to_rgb(hue / 255.0, sat / 255.0, val / 255.0)
        return (
            int(rgb[0] * 255) & 0xFF,
            int(rgb[1] * 255) & 0xFF,
            int(rgb[2] * 255) & 0xFF,
        )

    @staticmethod
    def nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges=24):
        """Blend currentPalette toward targetPalette."""
        current = list(currentPalette)
        target = list(targetPalette)
        changes = 0

        # Each color is a tuple (r, g, b), so flatten both palettes to lists of channels
        def flatten(palette):
            flat = []
            for color in palette:
                if isinstance(color, int):
                    # Convert hex to (r, g, b)
                    color = ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)
                flat.extend(color)
            return flat

        def unflatten(flat, length):
            return [tuple(flat[i : i + 3]) for i in range(0, length, 3)]

        flat_current = flatten(current)
        flat_target = flatten(target)
        totalChannels = min(len(flat_current), len(flat_target))

        for i in range(totalChannels):
            if flat_current[i] == flat_target[i]:
                continue
            if flat_current[i] < flat_target[i]:
                flat_current[i] += 1
                changes += 1
            elif flat_current[i] > flat_target[i]:
                flat_current[i] -= 1
                changes += 1
                if flat_current[i] > flat_target[i]:
                    flat_current[i] -= 1
            if changes >= maxChanges:
                break

        # Rebuild palette as tuple of (r, g, b)
        return tuple(unflatten(flat_current, len(flat_current)))

    @classmethod
    def getAverageLight(cls, crgb):
        eightyFive = 85  # dont ask
        return (
            cls.scale8(crgb[0], eightyFive)
            + cls.scale8(crgb[1], eightyFive)
            + cls.scale8(crgb[2], eightyFive)
        )

    @staticmethod
    def scale8(value, scale):
        return ((int(value) & 0xFFFF) * ((int(scale) & 0xFFFF) + 1)) >> 8

    @staticmethod
    def scale16(value, scale):
        return ((int(value) & 0xFFFF) * (int(scale) & 0xFFFF)) >> 16

    @classmethod
    def CRGB_nscale8(cls, rgb: tuple, scaledown: int):
        r = ((rgb[0]) * (scaledown + 1)) >> 8
        g = ((rgb[1]) * (scaledown + 1)) >> 8
        b = ((rgb[2]) * (scaledown + 1)) >> 8
        return (r & 0xFF, g & 0xFF, b & 0xFF)

    @staticmethod
    def qaddint(a, b, lim=0xFF):
        """Add b to a, ensuring the result does not exceed 255."""
        return min(lim, a + b)

    @staticmethod
    def qsubint(a, b):
        """Subtract b from a, ensuring the result is not negative."""
        return int(max(0, a - b))

    @classmethod
    def ColorFromPalette(
        cls,
        palette: tuple,
        index: int,
        brightness: int = 255,
        blending: str = "NOBLEND",
    ):
        if not palette:
            return (0, 0, 0)

        if blending == "LINEARBLEND" and len(palette) > 1:
            # Ultra-smooth linear blending with higher precision for eliminating choppiness
            palette_scale = len(palette) - 1
            scaled_index = (
                index * palette_scale * 256
            ) / 255.0  # Higher precision calculation

            # Get the two adjacent palette entries to blend between
            palette_index1 = int(scaled_index // 256) % len(palette)
            palette_index2 = (palette_index1 + 1) % len(palette)

            # Calculate blend ratio with higher precision (0-255)
            blend_ratio = int(scaled_index % 256) & 0xFF

            # Get colors and convert from hex if needed
            color1 = palette[palette_index1]
            color2 = palette[palette_index2]

            if isinstance(color1, int):
                color1 = ((color1 >> 16) & 0xFF, (color1 >> 8) & 0xFF, color1 & 0xFF)
            if isinstance(color2, int):
                color2 = ((color2 >> 16) & 0xFF, (color2 >> 8) & 0xFF, color2 & 0xFF)

            # Blend the two colors with high precision
            red1 = cls.blend8(color1[0], color2[0], blend_ratio)
            green1 = cls.blend8(color1[1], color2[1], blend_ratio)
            blue1 = cls.blend8(color1[2], color2[2], blend_ratio)
        else:
            # Original discrete palette lookup
            hi4 = index >> 4
            palette_index = hi4 % len(palette)

            color = palette[palette_index]
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

        partial += b * amountB
        partial -= a * amountB

        return (partial >> 8) & 0xFF

    @staticmethod
    def blend(c1, c2, amountC2):
        """Blend two colors c1 and c2 by amountC2 (0-255)."""
        r = FastLEDFunctions.blend8(c1[0], c2[0], amountC2)
        g = FastLEDFunctions.blend8(c1[1], c2[1], amountC2)
        b = FastLEDFunctions.blend8(c1[2], c2[2], amountC2)
        return (r, g, b)

    @staticmethod
    def random8(min=0, lim=0xFF):
        min = int(min) & 0xFF
        lim = int(lim) & 0xFF
        return random.randint(min, lim)

    @staticmethod
    def random16(min=0, lim=0xFFFF):
        min = int(min) & 0xFFFF
        lim = int(lim) & 0xFFFF
        return random.randint(min, lim)

    @classmethod
    def HeatColor(cls, temperature: int):
        """Convert a temperature value (0-255) to a color."""
        temperature = int(temperature) & 0xFF
        color = [0, 0, 0]

        # scale heat from 0-255 to 0-191
        scaled = cls.scale8(temperature, 0xBF)

        heatramp = scaled & 0x3F  # 0-63
        heatramp <<= 2  # 0-252

        if scaled & 0x80:
            # hottest third of 0xBF
            color[0] = 255
            color[1] = 255
            color[2] = heatramp
        elif scaled & 0x40:
            # middle third of 0xBF
            color[0] = 255
            color[1] = heatramp
            color[2] = 0
        else:
            # coolest third of 0xBF
            color[0] = heatramp
            color[1] = 0
            color[2] = 0
        return tuple(color)

    @classmethod
    def beat88(cls, bpm_88, timebase_32b=0):
        bpm_88 &= 0xFFFF
        timebase_32b &= 0xFFFFFFFF
        return (
            ((int(time.time() * 1000) - timebase_32b) * bpm_88 * 280) >> 16
        ) & 0xFFFF

    @classmethod
    def beat16(cls, bpm_88, timebase_32b=0):
        return cls.beat88(bpm_88, timebase_32b)

    @classmethod
    def beat8(cls, bpm_88, timebase_32b=0):
        return cls.beat16(bpm_88, timebase_32b) >> 8

    # Pre-computed sine lookup tables for performance
    _sin16_table = None
    _sin8_table = None

    @classmethod
    def _init_sin_tables(cls):
        if cls._sin16_table is None:
            cls._sin16_table = [
                int(math.sin((i / 65536.0) * (2 * math.pi)) * 32767)
                for i in range(65536)
            ]
        if cls._sin8_table is None:
            cls._sin8_table = [
                int(math.sin((i / 256.0) * (2 * math.pi)) * 127 + 128)
                for i in range(256)
            ]

    @staticmethod
    def sin16(theta):
        """
        Fast 16-bit sine using lookup table.
        """
        if FastLEDFunctions._sin16_table is None:
            FastLEDFunctions._init_sin_tables()
        theta &= 0xFFFF
        return FastLEDFunctions._sin16_table[theta]

    @staticmethod
    def sin8(theta_8b):
        """
        Fast 8-bit sine using lookup table.
        """
        if FastLEDFunctions._sin8_table is None:
            FastLEDFunctions._init_sin_tables()
        theta_8b &= 0xFF
        return FastLEDFunctions._sin8_table[theta_8b]

    @classmethod
    def beatsin88(
        cls,
        bpm_88,
        lowest_16b=0,
        highest_16b=0xFFFF,
        timebase_32b=0,
        phase_offset_16b=0,
    ):
        bpm_88 &= 0xFFFF
        lowest_16b &= 0xFFFF
        highest_16b &= 0xFFFF
        timebase_32b &= 0xFFFFFFFF
        phase_offset_16b &= 0xFFFF

        beat = cls.beat88(bpm_88, timebase_32b)
        beatsin = cls.sin16(beat + phase_offset_16b) + 32768
        scaledbeat = cls.scale16(beatsin, highest_16b - lowest_16b)
        return (lowest_16b + scaledbeat) & 0xFFFF

    @classmethod
    def beatsin16(
        cls,
        bpm_88,
        lowest_16b=0,
        highest_16b=0xFFFF,
        timebase_32b=0,
        phase_offset_16b=0,
    ):
        bpm_88 &= 0xFFFF
        lowest_16b &= 0xFFFF
        highest_16b &= 0xFFFF
        timebase_32b &= 0xFFFFFFFF
        phase_offset_16b &= 0xFFFF

        beat = cls.beat16(bpm_88, timebase_32b)
        beatsin = (cls.sin16(beat + phase_offset_16b) + 32768) & 0xFFFF
        scaledbeat = cls.scale16(beatsin, highest_16b - lowest_16b) & 0xFFFF
        return (lowest_16b + scaledbeat) & 0xFFFF

    @classmethod
    def beatsin8(
        cls, bpm_88, lowest_8b=0, highest_8b=0xFF, timebase_32b=0, phase_offset_8b=0
    ):
        bpm_88 &= 0xFFFF
        lowest_8b &= 0xFF
        highest_8b &= 0xFF
        timebase_32b &= 0xFFFFFFFF
        phase_offset_8b &= 0xFF

        beat = cls.beat8(bpm_88, timebase_32b)
        beatsin = cls.sin8(beat + phase_offset_8b)
        scaledbeat = cls.scale8(beatsin, highest_8b - lowest_8b)
        return (lowest_8b + scaledbeat) & 0xFF

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


class LEDThemes:
    _instance = None

    def __init__(self):
        assert LEDThemes._instance is None, "LEDThemes instance already exists"
        LEDThemes._instance = self
        self.themes = {
            "null": LEDThemes.null()
        }  # needs to init like this because `self._checkLoopExists` references it
        self.themes = {
            "ledSelector": self.ledSelector(),
            "rainbow": self.rainbow(),
            "fire2012": self.fire2012(),
            "rgbSnake": self.rgbSnake(),
            "twinkle": self.twinkle(),
            "pacifica": self.pacifica(),
            "epilepsy": self.epilepsy(),
            "freaky": LEDTheme("freaky"),
        }

    @classmethod
    def _checkAssr(cls):
        """
        Check if the LEDThemes instance is initialized.
        Raises an AssertionError if not initialized.
        """
        assert cls._instance, "LEDThemes instance not initialized"

    @classmethod
    def getInstance(cls):
        cls._checkAssr()
        return cls._instance

    @classmethod
    def getTheme(cls, loop_id: str = None):
        cls._checkAssr()
        return cls._instance.themes.get(loop_id)

    @classmethod
    def getAllThemes(cls):
        cls._checkAssr()
        return cls._instance.themes.values()

    @staticmethod
    def null():
        return LEDTheme("null")

    def _checkThemeExists(self, theme_id: str):
        assert (
            theme_id not in self.themes.keys()
        ), f"LED theme '{theme_id}' already exists"

    def ledSelector(self):
        self._checkThemeExists("ledSelector")

        num = ctk.IntVar(value=0)

        def target(theme: "LEDTheme"):
            for i in range(theme.strip.numPixels()):
                c = 255 if i == num.get() else 0
                theme.strip.setPixelColor(i, ws.Color(c, c, c))
            theme.strip.show()

        def uiMaker(theme: "LEDTheme", ui: CommandUI, withShowSaveButton: callable):
            ui.add(
                ctk.CTkLabel,
                "l_num",
                textvariable=num,
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_num",
                variable=num,
                from_=0,
                to=theme.leds.numPixels() - 1,
                number_of_steps=theme.leds.numPixels() - 2,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("num", num.get())
                )
            )

        return LEDTheme(
            "ledSelector",
            settingsUIFactory=uiMaker
        )
    
    def epilepsy(self):
        self._checkThemeExists("epilepsy")

        return LEDTheme(
            "epilepsy"
        )

    def rainbow(self, *, _name="rainbow"):
        self._checkThemeExists(_name)

        iterations = ctk.IntVar(value=10)
        delay = ctk.IntVar(value=30)
        step_size = ctk.IntVar(value=4)

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            ui.add(
                ctk.CTkLabel,
                "l_iterations",
                text="Pattern Sparseness",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_iterations",
                variable=iterations,
                from_=1,
                to=100,
                number_of_steps=99,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("iterations", iterations.get())
                )
            )
            ui.add(
                ctk.CTkLabel,
                "l_stepSize",
                text="Step Size",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_step_size",
                variable=step_size,
                from_=1,
                to=32,
                number_of_steps=31,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("stepSize", step_size.get())
                )
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/rainbow.png",
            friendlyName="Rainbow",
        )

    def fire2012(self, *, _name="fire2012"):
        self._checkThemeExists(_name)

        cooling = ctk.IntVar(value=30)
        sparking = ctk.IntVar(value=130)
        reversed = ctk.BooleanVar(value=False)
        _cooling = cooling.get()
        _sparking = sparking.get()
        _reversed = reversed.get()

        temps = None

        def target(self: "LEDTheme"):
            nonlocal temps

            nonlocal _cooling, _sparking, _reversed
            if isinstance(cooling, ctk.IntVar):
                _cooling = cooling.get()
            if isinstance(sparking, ctk.IntVar):
                _sparking = sparking.get()
            if isinstance(reversed, ctk.BooleanVar):
                _reversed = reversed.get()

            if temps is None:
                temps = [0] * self.strip.numPixels()
            # cool cells
            for i in range(self.strip.numPixels()):
                temps[i] = (
                    FastLEDFunctions.qsubint(
                        temps[i],
                        FastLEDFunctions.random8(
                            0, ((_cooling * 10) / self.strip.numPixels()) + 2
                        ),
                    )
                    & 0xFF
                )
            # heat up randomly
            reversePixelsRange = list(range(self.strip.numPixels() - 1))[::-1][:-1]
            for k in reversePixelsRange:
                temps[k] = int((temps[k - 1] + temps[k - 2] + temps[k - 2]) / 3) & 0xFF

            if FastLEDFunctions.random8(0, 0xFF) < _sparking:
                random_sparked = FastLEDFunctions.random8(lim=7)
                temps[random_sparked] = FastLEDFunctions.qaddint(
                    temps[random_sparked],
                    FastLEDFunctions.random8(160, 255),
                    0xFF,
                )

            for i in range(self.strip.numPixels()):
                color = FastLEDFunctions.HeatColor(temps[i])
                if _reversed:
                    self.strip.setPixelColor(
                        self.strip.numPixels() - 1 - i, ws.Color(*color)
                    )
                else:
                    self.strip.setPixelColor(i, ws.Color(*color))
            if self.checkBreak():
                return True
            self.strip.show()

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            ui.add(ctk.CTkLabel, "l_cooling", text="Cooling", font=("Arial", 20)).grid(
                row=0, column=0, padx=20, pady=15, sticky="nsw"
            )
            ui.add(
                ctk.CTkSlider,
                "s_cooling",
                variable=cooling,
                from_=0,
                to=255,
                number_of_steps=254,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(lambda *_: theme.setData("cooling", cooling.get()))
            )

            ui.add(
                ctk.CTkLabel, "l_sparking", text="Sparking", font=("Arial", 20)
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_sparking",
                variable=sparking,
                from_=0,
                to=255,
                number_of_steps=254,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(lambda *_: theme.setData("sparking", sparking.get()))
            )

            ui.add(
                ctk.CTkCheckBox,
                "c_reversed",
                variable=reversed,
                text="Reverse",
            ).grid(
                row=2, columnspan=2, padx=(20, 20), pady=(0, 15), sticky="nsew"
            ).setCommand(
                withShowSaveButton(lambda *_: theme.setData("reversed", reversed.get()))
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/fire.png",
            friendlyName="Fireplace",
        )

    def rgbSnake(self, *, _name="rgbSnake"):
        self._checkThemeExists(_name)

        tailScaleFactor = ctk.IntVar(value=250)
        step_size = ctk.IntVar(value=1)  # pixels to skip

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            ui.add(
                ctk.CTkLabel,
                "l_tailScaleFactor",
                text="Tail Length",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_tailScaleFactor",
                variable=tailScaleFactor,
                from_=0,
                to=255,
                number_of_steps=249,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("tailScaleFactor", tailScaleFactor.get())
                )
            )
            ui.add(
                ctk.CTkLabel,
                "l_step_size",
                text="Snake Speed",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_step_size",
                variable=step_size,
                from_=1,
                to=7,
                number_of_steps=8,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("stepSize", step_size.get())
                )
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/snake.png",
            friendlyName="Color Snake",
        )

    def pacifica(self, *, _name="pacifica"):
        self._checkThemeExists(_name)

        return LEDTheme(
            _name,
            imagePath="assets/images/ocean.png",
            friendlyName="Ocean Blue",
        )

    def twinkle(self, *, _name="twinkle"):
        """
        [TODO] describe
        Originally wrote for Arduino but adapted for Python.
        """
        palettes = [
            Palette(
                "Purple",
                {
                    "purple1": 0x7A0DAF,
                    "purple2": 0x9B2BFF,
                    "purple3": 0xD466FF,
                    "pink1": 0xFF66CC,
                    "pink2": 0xFF33AA,
                    "violet": 0x7F00FF,
                    "magenta": 0xFF00FF,
                    "deep_purple": 0x3A0060,
                },
                [
                    "purple1",
                    "purple3",
                    "pink1",
                    "magenta",
                    "pink2",
                    "purple2",
                    "violet",
                    "deep_purple",
                    "magenta",
                    "pink1",
                    "purple3",
                    "pink2",
                    "purple1",
                    "violet",
                    "magenta",
                    "purple2",
                ],
            ),
            Palette(
                "C9",
                {
                    "red": 0xBB80400,
                    "orange": 0x902C02,
                    "green": 0x046002,
                    "blue": 0x070758,
                    "white": 0x606820,
                },
                [
                    "red",
                    "orange",
                    "red",
                    "orange",
                    "orange",
                    "red",
                    "orange",
                    "red",
                    "green",
                    "green",
                    "green",
                    "green",
                    "blue",
                    "blue",
                    "blue",
                    "white",
                ],
            ),
            Palette(
                "Blue and White",
                {"blue": 0x00000FF, "gray": 0x808080},
                [
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "blue",
                    "gray",
                    "gray",
                    "gray",
                ],
            ),
            Palette(
                "Rainbow",
                palette=[
                    0xFF0000,
                    0xD52A00,
                    0xAB5500,
                    0xAB7F00,
                    0xABAB00,
                    0x56D500,
                    0x00FF00,
                    0x00D52A,
                    0x00AB55,
                    0x0056AA,
                    0x0000FF,
                    0x2A00D5,
                    0x5500AB,
                    0x7F0081,
                    0xAB0055,
                    0xD5002B,
                ],
            ),
            Palette(
                "Fairy Lights",
                {
                    "fairy": 0xFFE42D,
                    "half-fairy": int((0xFFE42D & 0xFEFEFE) / 2) & 0xFFFFFF,
                    "quarter-fairy": int((0xFFE42D & 0xFCFCFC) / 4) & 0xFFFFFF,
                },
                [
                    "fairy",
                    "fairy",
                    "fairy",
                    "fairy",
                    "half-fairy",
                    "half-fairy",
                    "fairy",
                    "fairy",
                    "quarter-fairy",
                    "quarter-fairy",
                    "fairy",
                    "fairy",
                    "fairy",
                    "fairy",
                    "fairy",
                    "fairy",
                ],
            ),
            Palette(
                "Red Green White",
                {
                    "red": 0xFF0000,
                    "gray": 0x808080,
                    "green": 0x00FF00,
                },
                [
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "red",
                    "gray",
                    "gray",
                    "green",
                    "green",
                    "green",
                    "green",
                ],
            ),
            Palette(
                "Party Colors",
                palette=[
                    0x5500AB,
                    0x84007C,
                    0xB5004B,
                    0xE5001B,
                    0xE81700,
                    0xB84700,
                    0xAB7700,
                    0xABAB00,
                    0xAB5500,
                    0xDD2200,
                    0xF2000E,
                    0xC2003E,
                    0x8F0071,
                    0x5F00A1,
                    0x2F00D0,
                    0x0007F9,
                ],
            ),
            # Palette(
            #     "Red and White",
            #     {
            #         "red": 0xFF0000,
            #         "gray": 0x808080,
            #     },
            #     [
            #         "red",
            #         "red",
            #         "red",
            #         "red",
            #         "gray",
            #         "gray",
            #         "gray",
            #         "gray",
            #         "red",
            #         "red",
            #         "red",
            #         "red",
            #         "gray",
            #         "gray",
            #         "gray",
            #         "gray",
            #     ],
            # ),
            # Palette(
            #     "Snow",
            #     {
            #         "soft": 0x304048,
            #         "bright": 0xE0F0FF,
            #     },
            #     [
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "soft",
            #         "bright",
            #     ],
            # ),
            Palette(
                "Holly",
                {
                    "green": 0x00580C,
                    "red": 0xB00402,
                },
                [
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "green",
                    "red",
                ],
            ),
            Palette(
                "Ice Blue",
                {
                    "Ice_Blue1": 0x0C1040,
                    "Ice_Blue2": 0x182080,
                    "Ice_Blue3": 0x5080C0,
                },
                [
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue1",
                    "Ice_Blue2",
                    "Ice_Blue2",
                    "Ice_Blue2",
                    "Ice_Blue3",
                ],
            ),
        ]

        twinkleSpeed = ctk.IntVar(value=5)  # 1-8
        twinkleDensity = ctk.IntVar(value=4)  # 1-8
        secondsPerPallette = ctk.IntVar(value=60)  # seconds
        coolLikeIncandescent = ctk.BooleanVar(value=True)
        _twinkleSpeed = 5
        _twinkleDensity = 4
        _secondsPerPallette = 30
        _coolLikeIncandescent = True

        rawPalettes = [p.get() for p in palettes]
        currentIndex = 0
        targetPalette = rawPalettes[currentIndex]
        currentPalette = (0x000000,) * len(targetPalette)

        ms_0 = int(time.time() * 1000)
        blendCallRunning = False
        paletteSwapCallRunning = False

        def init(self: "LEDTheme", isRefreshOnly=False):
            nonlocal currentIndex, targetPalette, currentPalette, blendCallRunning, paletteSwapCallRunning
            nonlocal palettes, rawPalettes

            # Initialize the first palette
            rawPalettes = [p.get() for p in palettes]
            currentIndex = 0
            targetPalette = (
                rawPalettes[currentIndex] if rawPalettes else [(0, 0, 0)] * 16
            )
            currentPalette = (0x000000,) * len(targetPalette)

            if isRefreshOnly:
                return

            data = self.getData()
            twinkleSpeed.set(data.get("twinkleSpeed", _twinkleSpeed))
            twinkleDensity.set(data.get("twinkleDensity", _twinkleDensity))
            secondsPerPallette.set(data.get("secondsPerPallette", _secondsPerPallette))
            coolLikeIncandescent.set(
                data.get("coolLikeIncandescent", _coolLikeIncandescent)
            )

            blendCallRunning = False
            paletteSwapCallRunning = False

        def target(self: "LEDTheme"):
            # Early exit check - this should make switching faster
            if self.checkBreak():
                return True

            nonlocal blendCallRunning, paletteSwapCallRunning, currentPalette, targetPalette, ms_0

            nonlocal twinkleSpeed, twinkleDensity, secondsPerPallette, coolLikeIncandescent
            nonlocal _twinkleSpeed, _twinkleDensity, _secondsPerPallette, _coolLikeIncandescent
            if isinstance(twinkleSpeed, ctk.IntVar):
                _twinkleSpeed = twinkleSpeed.get()
            if isinstance(twinkleDensity, ctk.IntVar):
                _twinkleDensity = twinkleDensity.get()
            if isinstance(secondsPerPallette, ctk.IntVar):
                _secondsPerPallette = secondsPerPallette.get()
            if isinstance(coolLikeIncandescent, ctk.BooleanVar):
                _coolLikeIncandescent = coolLikeIncandescent.get()

            def swap_palette():
                if self.checkBreak():
                    return True
                nonlocal currentIndex, targetPalette
                currentIndex = (currentIndex + 1) % len(rawPalettes)
                targetPalette = rawPalettes[currentIndex]
                self.after(1000 * _secondsPerPallette, swap_palette)

            def blend_target():
                if self.checkBreak():
                    return True
                nonlocal currentPalette, targetPalette
                currentPalette = FastLEDFunctions.nblendPaletteTowardPalette(
                    currentPalette, targetPalette, 12
                )
                self.after(10, blend_target)

            if not blendCallRunning:
                blend_target()
                blendCallRunning = True
            if not paletteSwapCallRunning:
                self.after(1000 * _secondsPerPallette, swap_palette)
                paletteSwapCallRunning = True

            rng_16b = 11337
            clock_32b = (int)(time.time() * 1000) - ms_0

            bg = (0, 0, 0)

            bgBrightness_8b = FastLEDFunctions.getAverageLight(bg) & 0xFF

            for i in range(self.strip.numPixels()):
                if self.checkBreak():
                    return True

                rng_16b = (rng_16b * 2053) + 1384
                rng_16b &= 0xFFFF  # Ensure PRNG16 is 16 bits
                clockOffset_16b = rng_16b & 0xFFFF
                rng_16b = (rng_16b * 2053) + 1384
                rng_16b &= 0xFFFF  # Ensure PRNG16 is 16 bits

                # use that number as clock speed adjustment factor (in 8ths, from 8/8ths, to 23/8ths)
                speedMultiplier_8b = (
                    ((((rng_16b & 0xFF) >> 4) + (rng_16b & 0x0F)) & 0x0F) + 0x08
                ) & 0xFF
                clock30_32b = (
                    ((clock_32b * speedMultiplier_8b) >> 3) + clockOffset_16b
                ) & 0xFFFFFFFF  # 32 bit
                unique_8b = (rng_16b >> 8) & 0xFF  # salt for pixel

                ms_32b = clock30_32b & 0xFFFFFFFF
                salt = unique_8b

                ticks_16b = (ms_32b >> (8 - _twinkleSpeed)) & 0xFFFF
                fastCycle_8b = ticks_16b & 0xFF
                slowCycle_16b = ((ticks_16b >> 8) + salt) & 0xFFFF

                slowCycle_16b += int(math.sin(slowCycle_16b) * 255) + 128
                slowCycle_16b &= 0xFFFF
                slowCycle_16b = (slowCycle_16b * 2053) + 1384
                slowCycle_16b &= 0xFFFF
                slowCycle_8b = ((slowCycle_16b & 0xFF) + (slowCycle_16b >> 8)) & 0xFF

                bright_8b = 0
                if (slowCycle_8b & 0x0E) / 2 < _twinkleDensity:
                    copy = fastCycle_8b
                    if copy < 86:
                        bright_8b = copy * 3
                    else:
                        copy -= 86
                        # Fix: Ensure brightness calculation doesn't go negative or wrap around
                        adjustment = min(
                            copy, 169
                        )  # Cap the adjustment to prevent negative results
                        bright_8b = 255 - adjustment
                    # Ensure brightness stays within valid range
                    bright_8b = max(0, min(255, bright_8b)) & 0xFF

                hue_8b = (slowCycle_8b - salt) & 0xFF
                outputColor = (0, 0, 0)
                if bright_8b > 0:
                    outputColor = FastLEDFunctions.ColorFromPalette(
                        currentPalette, hue_8b, bright_8b
                    )
                    if _coolLikeIncandescent:
                        if fastCycle_8b >= 128:
                            cooling = ((fastCycle_8b - 128) >> 4) & 0xFF
                            g = max(outputColor[1] - cooling, 0)
                            b = max(outputColor[2] - (cooling * 2), 0)
                            outputColor = (outputColor[0], g, b)

                outputBrightAvg_8b = (
                    FastLEDFunctions.getAverageLight(outputColor) & 0xFF
                )
                deltaBright_8b = (outputBrightAvg_8b - bgBrightness_8b) & 0xFF
                if deltaBright_8b >= 32 or not bg:
                    self.strip.setPixelColor(i, ws.Color(*outputColor))
                elif deltaBright_8b > 0:
                    self.strip.setPixelColor(
                        i,
                        ws.Color(
                            *FastLEDFunctions.blend(bg, outputColor, deltaBright_8b * 8)
                        ),
                    )
                else:
                    self.strip.setPixelColor(i, ws.Color(*bg))
            self.strip.show()

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            nonlocal twinkleSpeed, twinkleDensity, secondsPerPallette, coolLikeIncandescent
            nonlocal palettes

            sui = SwappableUI(ui.master)
            sui.grid(row=0, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")
            f_sliders = sui.addFrame("sliders")
            f_sliders.grid_columnconfigure(0, weight=0)
            f_sliders.grid_columnconfigure(1, weight=1)
            ui.add(
                ctk.CTkLabel,
                "l_speed",
                root=f_sliders,
                text="Speed (1-8):",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=(0, 20), pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_speed",
                root=f_sliders,
                from_=1,
                to=8,
                number_of_steps=7,
                height=30,
                variable=twinkleSpeed,
            ).grid(row=0, column=1, padx=0, pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("twinkleSpeed", twinkleSpeed.get())
                )
            )
            ui.add(
                ctk.CTkLabel,
                "l_density",
                root=f_sliders,
                text="Density (1-8):",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=(0, 20), pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_density",
                root=f_sliders,
                from_=1,
                to=8,
                number_of_steps=7,
                height=30,
                variable=twinkleDensity,
            ).grid(row=1, column=1, padx=0, pady=15, sticky="nsew").setCommand(
                withShowSaveButton(
                    lambda *_: theme.setData("twinkleDensity", twinkleDensity.get())
                )
            )
            ui.add(
                ctk.CTkButton,
                "b_palettes",
                root=f_sliders,
                text="Palettes",
                command=lambda: sui.setFrame("palettes"),
            ).grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="nsew")

            f_palettes = sui.addFrame("palettes")
            ui.add(
                ctk.CTkButton,
                "b_back",
                root=f_palettes,
                text="Back",
                command=lambda: sui.setFrame("sliders"),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsew")
            ui.add(
                ctk.CTkButton,
                "b_add_random",
                root=f_palettes,
                text="Add Random Palette",
                command=lambda: (
                    palettes.append(
                        Palette(
                            "Random Palette",
                            palette=[
                                ((r << 16) & 0xFF | (g << 8) & 0xFF | b & 0xFF)
                                for (r, g, b) in [
                                    FastLEDFunctions.fromHSV(
                                        random.randint(0, 255),  # hue
                                        random.randint(
                                            220, 255
                                        ),  # saturation (avoid white)
                                        random.randint(160, 220),  # value (avoid black)
                                    )
                                    for _ in range(4)
                                ]
                            ]
                            * 4,
                        ),
                    ),
                    theme._initTarget(theme, True),
                ),
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsew")
            ui.add(
                ctk.CTkButton,
                "b_clear",
                root=f_palettes,
                text="Clear Palettes",
                command=lambda: (
                    palettes.clear(),
                    theme._initTarget(theme, True),
                ),
            ).grid(row=2, column=0, padx=20, pady=15, sticky="nsew")

            sui.setFrame("sliders")

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/christmas.png",
            friendlyName="Christmas",
        )


class Palette:
    def __init__(self, name, colors=[], palette=None):
        self.name = name
        self.colors = colors
        self.palette = []

        if colors != [] and palette:
            self.palette = [self.colors[i] for i in palette]
        elif colors == []:
            self.palette = palette if palette else []

    def get(self):
        return tuple(self.palette)
