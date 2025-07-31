from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import threading
import time
import traceback
import rpi_ws281x as ws

from LEDLoops import LEDLoops
from lib.led.LEDLoop import LEDLoop

class LEDService:
    _instance = None

    LED_COUNT = 300
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 255 # 0-255
    LED_INVERT = False
    LED_CHANNEL = 0

    def __init__(self, appRoot: 'App'):
        if LEDService._instance is not None:
            raise RuntimeError("LEDService is a singleton and cannot be instantiated multiple times.")
        self.leds = ws.PixelStrip(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            self.LED_BRIGHTNESS,
            self.LED_CHANNEL
        )
        self.leds.begin()

        self.appRoot: 'App' = appRoot

        LEDLoops() # initialize all LED loops
        self.loop = LEDLoops.null()

        self._breakLoopEvent = threading.Event()
        self._isInLoop = False
        self._isChangingLoop = False
        self._hasChangeTimedOut = False
        self.loopThread = None

        self.errorCallback = lambda e: print(e)

        self._createLoopThread()
        self.loopThread.start()

        LEDService._instance = self

    def _createLoopThread(self):
        self.loopThread = threading.Thread(target=self._ledLoopTarget, daemon=True)

    def _ledLoopTarget(self):
        self._isInLoop = True
        self.loop.passApp(self.appRoot)
        self.loop.passArgs(self.leds, self._breakLoopEvent)
        self.loop.runInit()
        while not self._breakLoopEvent.is_set():
            time.sleep(0.005)  # Sleep to prevent busy waiting
            try:
                stat = self.loop.runLoop()
                if stat is not None:
                    # print("finished " + self.loop.id)
                    self._breakLoopEvent.set()
                    break
            except Exception:
                self.errorCallback(traceback.format_exc())
                break
        self._isInLoop = False
        
    def setLoop(self, loop: 'LEDLoop' = None):
        # ensure this is not called multiple times
        if self._isChangingLoop and not self._hasChangeTimedOut:
            return
        
        if not loop:
            loop = LEDLoops.null()

        if loop.id == self.loop.id and not self._isChangingLoop:
            return
        
        self._breakLoopEvent.set()
        
        if self._hasChangeTimedOut:
            self._hasChangeTimedOut = False

        self._isChangingLoop = True

        timeout = time.time() + 2
        while self._isInLoop and time.time() < timeout:
            time.sleep(0.1)

        if self._isInLoop:
            try:
                self._hasChangeTimedOut = True
                raise RuntimeError("LED loop is still running after 2 seconds. This should not happen!")
            except:
                self.errorCallback(traceback.format_exc())
            return

        self._breakLoopEvent.clear()

        if not loop:
            loop = LEDLoops.null()
        self.loop = loop

        self._createLoopThread()
        self.loopThread.start()

        self._isChangingLoop = False

    def setBrightness(self, brightness: int):
        self.leds.setBrightness(int(brightness) & 0xFF) # constrain brightness to 0-255
        self.leds.show()

    def setSolid(self, r: int, g: int, b: int):
        if self.loopThread:
            if self.loopThread.is_alive():
                self.setLoop(LEDLoops.null())
        for i in range(self.LED_COUNT):
            self.leds.setPixelColor(i, ws.Color(r, g, b))
        self.leds.show()
    
    def off(self):
        self.setSolid(0, 0, 0)

    @classmethod
    def getInstance(cls):
        return cls._instance
