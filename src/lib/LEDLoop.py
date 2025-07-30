import threading
import rpi_ws281x as ws

from lib.Navigation import NavigationPage

class LEDLoop:
    def __init__(self, id: str, loopTarget=lambda *_: 1, initTarget=lambda *_: None, settings: 'NavigationPage' = None):
        self.id = id

        # self._isFinished = False

        self.loopTarget = loopTarget
        self.initTarget = initTarget

        self.settings: NavigationPage = settings

        self.leds: 'ws.PixelStrip' = None
        self.break_event: 'threading.Event' = None
        self.after = lambda delay, callback: None

    def getSettings(self) -> 'NavigationPage':
        """
        Returns the settings page associated with this LED loop.
        """
        return self.settings

    def passArgs(self, leds: 'ws.PixelStrip', break_event: 'threading.Event'):
        self.leds = leds
        self.break_event = break_event

    def passAfterMethod(self, after_method: callable):
        """
        Passes the after method to the LEDLoop, which is used to schedule tasks.
        Should provide something like `customtkinter.CTk.after()`
        """
        self.after = after_method

    def checkBreak(self):
        """
        Checks if the break event is set.
        Returns True if the loop should stop, False otherwise.
        """
        return self.break_event.is_set()

    def setFinished(self):
        self._isFinished = True

    def isFinished(self) -> bool:
        return self._isFinished

    def runInit(self):
        """
        Runs the initialization target function.
        """
        if not self.initTarget:
            raise RuntimeError("LEDLoop target requires init method to be set.")

        return self.initTarget(self)

    def runLoop(self):
        """
        Runs the LED loop with the provided target function.
        """
        if not self.leds or not self.break_event:
            raise RuntimeError("LEDLoop must have leds and break_event set before running.")

        if not self.after:
            raise RuntimeError("LEDLoop target requires after method to be set.")

        return self.loopTarget(self)
