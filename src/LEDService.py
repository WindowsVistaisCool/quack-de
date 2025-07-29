import threading
import time
import traceback
from rpi_ws281x import PixelStrip as ws

from LEDLoops import LEDLoops

class LEDService:
    LED_COUNT = 300
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 255 # 0-255
    LED_INVERT = False
    LED_CHANNEL = 0

    def __init__(self):
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
        
        self.loop = LEDLoops.null()
        self._breakLoopEvent = threading.Event()
        self._isInLoop = False
        self._isChangingLoop = False
        self._hasChangeTimedOut = False
        self.loopThread = None

        self.loopErrCallback = lambda e: print(e)

        self._createLoopThread()
        self.loopThread.start()
    
    def _createLoopThread(self):
        self.loopThread = threading.Thread(target=self._ledLoopTarget, daemon=True)

    def _ledLoopTarget(self):
        self._isInLoop = True
        while not self._breakLoopEvent.is_set():
            time.sleep(0.05)  # Sleep to prevent busy waiting
            try:
                finished = self.loop(self.leds, self._breakLoopEvent)
                if finished is True:
                    self._breakLoopEvent.set()
            except Exception:
                self.loopErrCallback(traceback.format_exc())
                break
        self._isInLoop = False
        
    def setLoop(self, callable):
        self._breakLoopEvent.set()

        # ensure this is not called multiple times
        if self._isChangingLoop and not self._hasChangeTimedOut:
            return
        
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
                self.loopErrCallback(traceback.format_exc())
            return

        self._breakLoopEvent.clear()

        if not callable:
            callable = LEDLoops.null()
        self.loop = callable

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
