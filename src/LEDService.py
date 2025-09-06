from typing import TYPE_CHECKING

from lib.led.SocketLED import SocketLED

if TYPE_CHECKING:
    from App import App

from LEDThemes import LEDThemes

class LEDService:
    _instance = None

    def __init__(self, appRoot: "App"):
        if LEDService._instance is not None:
            raise RuntimeError(
                "LEDService is a singleton and cannot be instantiated multiple times."
            )
        self.leds = SocketLED()

        # self.leds.addSubStrip("Door Side", [(0, 124), (743, 822)])
        # self.leds.addSubStrip("Kyle Side", [(124, 324)])
        # self.leds.addSubStrip("Window", [(324, 534)])
        # self.leds.addSubStrip("Jusnoor Side", [(534, 743)])

        self.appRoot: "App" = appRoot

        LEDThemes()

        LEDService._instance = self

    @classmethod
    def getInstance(cls):
        return cls._instance
