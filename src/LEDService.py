from typing import TYPE_CHECKING

from lib.DevChecks import isDev
from lib.DevChecks import isDev
from lib.led.SocketLED import SocketLED

if TYPE_CHECKING:
    from App import App

from LEDThemes import LEDThemes
from lib.led.LEDTheme import LEDTheme

class LEDService:
    _instance = None

    def __init__(self, appRoot: "App"):
        if LEDService._instance is not None:
            raise RuntimeError(
                "LEDService is a singleton and cannot be instantiated multiple times."
            )
        self.leds = SocketLED()

        # if not isDev():
        # self.leds.begin()

        # self.leds.addSubStrip("Door Side", [(0, 124), (743, 822)])
        # self.leds.addSubStrip("Kyle Side", [(124, 324)])
        # self.leds.addSubStrip("Window", [(324, 534)])
        # self.leds.addSubStrip("Jusnoor Side", [(534, 743)])

        self.appRoot: "App" = appRoot

        # initialize themes registry
        LEDThemes()  # themes are initialized in this constructor

        self._errorCallback = lambda e: print(e)

        LEDService._instance = self

    def setLoop(self, loop: "LEDTheme" = None, subStrip="All"):
        """
        Start or replace a loop. If the theme has a stripID, it will run on that sub-strip
        (one thread per sub-strip). If stripID is None, it runs on the full strip (key=None).

        Passing None will set the null theme (which does not spawn a thread) for the key.
        """
        self.leds.setLoop(loop.id, subStrip)

    def setBrightness(self, brightness: int):
        pass

    def setSolid(self, r: int, g: int, b: int, subStrip=None):
        pass

    def off(self):
        pass

    @classmethod
    def getInstance(cls):
        return cls._instance
