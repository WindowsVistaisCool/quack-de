import rpi_ws281x as ws


class SegmentedPixelStrip(ws.PixelStrip):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subStrips = {}

    def addSubStrip(self, id: str, ranges: list):
        assert id not in self.subStrips.keys(), f"Sub-strip ID {id} already exists"
        assert id.lower() != "all", f"Sub-strip ID `{id}` is reserved"

        # for sub_strip in self.subStrips.values():
        #     overlap = not (end <= sub_strip.start or start >= sub_strip.end)
        #     assert (
        #         not overlap
        #     ), f"Sub-strip [{start}, {end}) overlaps with existing sub-strip [{sub_strip.start}, {sub_strip.end})"

        sub_strip = SubStrip(self, ranges)
        self.subStrips[id] = sub_strip
        return sub_strip

    def getSubStrip(self, id: str):
        assert id in self.subStrips.keys(), f"Sub-strip ID {id} not found"
        return self.subStrips[id]

    def getSubStripRanges(self):
        return [sub_strip.ranges for sub_strip in self.subStrips.values()]

    def getSubStripRangesStr(self):
        return [sub_strip.rangeStr for sub_strip in self.subStrips.values()]

    def clearSubStrips(self):
        self.subStrips.clear()


class SubStrip:
    def __init__(self, leds: SegmentedPixelStrip, ranges: list):
        self.leds = leds

        self._pixelColors = []

        self.configure(ranges)

    def configure(self, ranges: list):
        self.ranges = ranges
        self.rangeStr = ""
        for rng in self.ranges:
            self.rangeStr += f"{rng[0]}-{rng[1]}, "
        self.rangeStr = self.rangeStr.strip(", ")
        
        # map the real phyiscal indicies for the strip to a continuous range
        self._stripTranslations = []
        for rng in self.ranges:
            jLoop = range(rng[0], rng[1])
            if len(rng) == 3 and rng[2] is True:
                jLoop = reversed(jLoop)
            for j in jLoop:
                self._stripTranslations.append(j)

    def numPixels(self):
        pixels = 0
        for rng in self.ranges:
            pixels += rng[1] - rng[0]
        return pixels

    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order)."""
        self.leds.setPixelColor(self._stripTranslations[n], color)

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setPixelColor(n, ws.Color(red, green, blue, white))

    def getPixelColorRGB(self, n):
        """Get the RGB color of the LED at position n."""
        return self.leds.getPixelColorRGB(self._stripTranslations[n])

    def show(self):
        self.leds.show()
