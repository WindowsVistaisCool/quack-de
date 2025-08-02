from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import threading
import time
import traceback
import rpi_ws281x as ws

from LEDLoops import LEDThemes
from lib.led.LEDTheme import LEDTheme


class LEDService:
    _instance = None

    LED_COUNT = 300
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
        self.leds = ws.PixelStrip(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            self.LED_BRIGHTNESS,
            self.LED_CHANNEL,
        )
        self.leds.begin()

        self.appRoot: "App" = appRoot

        LEDThemes()  # initialize all LED loops
        self.loop = LEDThemes.null()

        self._breakLoopEvent = threading.Event()
        self._loopChangeEvent = threading.Event()
        self._isRunning = True
        self._isChangingLoop = False
        self._hasChangeTimedOut = False
        self.loopThread = None

        self.errorCallback = lambda e: print(e)

        # Create and start the single persistent thread
        self.loopThread = threading.Thread(target=self._ledLoopTarget, daemon=True)
        self.loopThread.start()

        LEDService._instance = self

    def _ledLoopTarget(self):
        while self._isRunning:
            # Wait for a loop to be set or service to stop
            if self.loop is None or self.loop.id == "null":
                time.sleep(0.01)
                continue

            # Ensure we're not in the middle of a loop change
            if self._isChangingLoop:
                time.sleep(0.01)
                continue

            # Initialize the current loop safely
            try:
                self.loop.passApp(self.appRoot)
                self.loop.passArgs(self.leds, self._breakLoopEvent)
                self.loop.runInit()
            except Exception:
                self.errorCallback(
                    f"Failed to initialize loop {self.loop.id}: {traceback.format_exc()}"
                )
                time.sleep(0.1)
                self.setLoop(LEDThemes.null())  # Reset to null loop on error
                continue

            # Run the loop until break or loop change
            while (
                not self._breakLoopEvent.is_set()
                and self._isRunning
                and not self._loopChangeEvent.is_set()
            ):
                time.sleep(0.001)
                try:
                    stat = self.loop.runLoop()
                    if stat is not None:
                        self._breakLoopEvent.set()
                        break
                except Exception:
                    self.errorCallback(traceback.format_exc())
                    self._breakLoopEvent.set()
                    break

            # Clear events for next loop
            self._breakLoopEvent.clear()
            self._loopChangeEvent.clear()

    def setLoop(self, loop: "LEDTheme" = None):
        # ensure this is not called multiple times
        if self._isChangingLoop and not self._hasChangeTimedOut:
            return

        if not loop:
            loop = LEDThemes.null()

        if loop.id == self.loop.id and not self._isChangingLoop:
            return

        self._isChangingLoop = True

        # Signal current loop to stop
        self._breakLoopEvent.set()
        self._loopChangeEvent.set()

        # Wait a bit longer for current loop iteration to finish cleanly
        time.sleep(0.05)

        # Set new loop
        self.loop = loop

        if self._hasChangeTimedOut:
            self._hasChangeTimedOut = False

        self._isChangingLoop = False

    def setBrightness(self, brightness: int):
        self.leds.setBrightness(int(brightness) & 0xFF)  # constrain brightness to 0-255
        self.leds.show()

    def setSolid(self, r: int, g: int, b: int):
        self.setLoop(LEDThemes.null())  # Switch to null loop to stop current loop
        for i in range(self.LED_COUNT):
            self.leds.setPixelColor(i, ws.Color(r, g, b))
        self.leds.show()

    def off(self):
        self.setSolid(0, 0, 0)

    def shutdown(self):
        """Gracefully shutdown the LED service"""
        self._isRunning = False
        self._breakLoopEvent.set()
        self._loopChangeEvent.set()
        if self.loopThread and self.loopThread.is_alive():
            self.loopThread.join(timeout=1.0)

    @classmethod
    def getInstance(cls):
        return cls._instance
