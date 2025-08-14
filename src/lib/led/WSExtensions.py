import rpi_ws281x as ws


class SegmentedPixelStrip(ws.PixelStrip):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subStrips = []

    def addSubStrip(self, start: int, end: int):
        for sub_strip in self.subStrips:
            overlap = not (end <= sub_strip.start or start >= sub_strip.end)
            assert (
                not overlap
            ), f"Sub-strip [{start}, {end}) overlaps with existing sub-strip [{sub_strip.start}, {sub_strip.end})"

        sub_strip = SubStrip(self, start, end)
        self.subStrips.append(sub_strip)
        return sub_strip

    def getSubStrip(self, index: int):
        assert (
            0 <= index < len(self.subStrips)
        ), f"Sub-strip index {index} out of bounds"
        return self.subStrips[index]

    def clearSubStrips(self):
        self.subStrips.clear()


class SubStrip:
    def __init__(self, leds: SegmentedPixelStrip, start: int = 0, end: int = None):
        self.leds = leds

        self._pixelColors = []

        end = end if end is not None else leds.numPixels()
        self.configure(start, end)

    def configure(self, start: int, end: int):
        self.start = start
        self.end = end

    def numPixels(self):
        return self.end - self.start

    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order)."""
        tf = n + self.start
        assert (
            self.start <= tf < self.end
        ), f"Pixel index {n} out of bounds for sub-strip [{self.start}, {self.end})"
        self.leds.setPixelColor(tf, color)

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setPixelColor(n, ws.Color(red, green, blue, white))

    def getPixelColorRGB(self, n):
        """Get the RGB color of the LED at position n."""
        tf = n + self.start
        assert (
            self.start <= tf < self.end
        ), f"Pixel index {n} out of bounds for sub-strip [{self.start}, {self.end})"
        return self.leds.getPixelColorRGB(tf)

    def show(self):
        self.leds.show()
