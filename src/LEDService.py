from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import threading
import time
import traceback
import rpi_ws281x as ws

from LEDThemes import LEDThemes
from lib.led.LEDTheme import LEDTheme
from lib.led.WSExtensions import SegmentedPixelStrip


class LEDService:
    _instance = None

    LED_COUNT = 822
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 255  # 0-255
    LED_INVERT = False
    LED_CHANNEL = 0

    def __init__(self, appRoot: "App"):
        if LEDService._instance is not None:
            raise RuntimeError(
                "LEDService is a singleton and cannot be instantiated multiple times."
            )
        self.leds = SegmentedPixelStrip(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            self.LED_BRIGHTNESS,
            self.LED_CHANNEL,
        )
        self.leds.begin()
        self.leds.addSubStrip("Door Side", [(0, 124), (743, 822)])
        self.leds.addSubStrip("Kyle Side", [(124, 324)])
        self.leds.addSubStrip("Window", [(324, 534)])
        self.leds.addSubStrip("Jusnoor Side", [(534, 743)])

        self.appRoot: "App" = appRoot

        # initialize themes registry
        LEDThemes()  # themes are initialized in this constructor

        # active_loops maps a strip key (int for sub-strip index, or None for full-strip)
        # to a dict containing: theme, thread, break_event
        self.active_loops = {}

        self._isRunning = True

        self._errorCallback = lambda e: print(e)

        LEDService._instance = self

    def _ledLoopTarget(
        self, theme: "LEDTheme", break_event: threading.Event, subStrip=None
    ):
        """
        Thread target for running a single LEDTheme on its assigned strip (or full strip).
        """
        try:
            if subStrip == "All":
                subStrip = None
            theme.passApp(self.appRoot)
            theme.passArgs(self.leds, break_event, subStrip=subStrip)
            theme.runInit()
        except Exception:
            self._errorCallback(
                f"Failed to initialize loop {theme.id}: {traceback.format_exc()}"
            )
            return

        while not break_event.is_set() and self._isRunning:
            time.sleep(0.001)
            try:
                stat = theme.runLoop()
                if stat is not None:
                    break_event.set()
                    break
            except Exception:
                self._errorCallback(traceback.format_exc())
                break_event.set()
                break

    def setLoop(self, loop: "LEDTheme" = None, subStrip=None):
        """
        Start or replace a loop. If the theme has a stripID, it will run on that sub-strip
        (one thread per sub-strip). If stripID is None, it runs on the full strip (key=None).

        Passing None will set the null theme (which does not spawn a thread) for the key.
        """
        if not loop:
            loop = LEDThemes.null()

        # If setting a loop for the full strip (subStrip is None), cancel all active sub-strip loops
        if subStrip is None or subStrip == "All":
            for k in list(self.active_loops.keys()):
                if k is not None:
                    existing = self.active_loops.get(k)
                    if existing:
                        try:
                            existing["break_event"].set()
                            existing["thread"].join(timeout=0.2)
                        except Exception:
                            pass
                        finally:
                            self.active_loops.pop(k, None)
        # If setting a loop for a sub-strip, cancel any active full-strip loop
        else:
            existing_full = self.active_loops.get(None)
            if existing_full:
                try:
                    existing_full["break_event"].set()
                    existing_full["thread"].join(timeout=0.2)
                except Exception:
                    pass
                finally:
                    self.active_loops.pop(None, None)

        # key is the sub-strip index; None represents the full strip
        key = subStrip if subStrip is not None else None

        # If the same loop is already running for this key, do nothing
        existing = self.active_loops.get(key)
        if existing and existing.get("theme") and loop.id == existing["theme"].id:
            return

        # Stop any existing loop on this key
        if existing:
            try:
                existing["break_event"].set()
                # give loop a moment to exit
                existing["thread"].join(timeout=0.2)
            except Exception:
                pass
            finally:
                self.active_loops.pop(key, None)

        if loop.id == LEDThemes.null().id:
            return

        break_event = threading.Event()
        t = threading.Thread(
            target=self._ledLoopTarget, args=(loop, break_event, subStrip), daemon=True
        )
        self.active_loops[key] = {
            "theme": loop,
            "thread": t,
            "break_event": break_event,
            "subStrip": subStrip,
        }
        t.start()

    def setBrightness(self, brightness: int):
        self.leds.setBrightness(int(brightness) & 0xFF)  # constrain brightness to 0-255
        self.leds.show()

    def setSolid(self, r: int, g: int, b: int, subStrip=None):
        self.setLoop(LEDThemes.null(), subStrip)
        lim = self.leds.numPixels()
        if subStrip is not None:
            subStrip = self.leds.getSubStrip(subStrip)
            lim = subStrip.numPixels()
        for i in range(lim):
            if subStrip is not None:
                subStrip.setPixelColorRGB(i, r, g, b)
            else:
                self.leds.setPixelColor(i, ws.Color(r, g, b))
        self.leds.show()

    def off(self):
        for loop in self.active_loops.values():
            loop["break_event"].set()

        for i in range(self.leds.subStrips.__len__()):
            self.setLoop(LEDThemes.null(), subStrip=i)

        self.setSolid(0, 0, 0)

    def shutdown(self):
        """Gracefully shutdown the LED service"""
        self._isRunning = False
        # signal and join all active loops
        for key, info in list(self.active_loops.items()):
            try:
                info["break_event"].set()
                if info["thread"].is_alive():
                    info["thread"].join(timeout=1.0)
            except Exception:
                pass
        self.active_loops.clear()

    @classmethod
    def getInstance(cls):
        return cls._instance
