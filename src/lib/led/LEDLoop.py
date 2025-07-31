from typing import Type
import customtkinter as ctk
import threading
import rpi_ws281x as ws

from lib.QuackApp import QuackApp
from lib.led.LEDLoopSettings import LEDLoopSettings

class LEDLoop:
    """
    LEDLoop is a class that encapsulates the logic for running a loop that controls an LED strip.
    It provides mechanisms for initialization, loop execution, settings UI integration, and graceful interruption.
    Attributes:
        id (str): Unique identifier for the LED loop.
        loopTarget (callable): The main function to be executed in the loop. Should accept the LEDLoop instance as its argument.
        initTarget (callable): Initialization function to be called before the loop starts. Should accept the LEDLoop instance as its argument.
        settingUIFactory (callable, optional): Factory function to create the settings UI for this loop.
        app (QuackApp): Reference to the main application, used for accessing app-level methods and properties.
        leds (ws.PixelStrip): The LED strip object to be controlled.
        break_event (threading.Event): Event used to signal the loop to stop execution.
        after (callable): Function to schedule callbacks after a delay, typically provided by the app.
    Methods:
        getSettings(app: QuackApp) -> LEDLoopSettings:
        passArgs(leds: ws.PixelStrip, break_event: threading.Event):
        passApp(app: QuackApp):
            Passes the application instance to the loop for accessing app-level functionality.
        checkBreak() -> bool:
            Checks if the break event is set, indicating the loop should stop.
        setFinished():
            Marks the loop as finished.
        isFinished() -> bool:
            Returns whether the loop has been marked as finished.
        runInit():
            Executes the initialization target function.
        runLoop():
            Executes the main loop target function.
    """
    def __init__(self, id: str, loopTarget=lambda *_: 1, initTarget=lambda *_: None, settingsUIFactory: callable = None):
        self.id = id

        self.loopTarget = loopTarget
        self.initTarget = initTarget

        self.settingUIFactory = settingsUIFactory

        self.app: 'QuackApp' = None

        self.leds: 'ws.PixelStrip' = None
        self.break_event: 'threading.Event' = None
        self.after = lambda delay, callback: None

    def getSettings(self, app: QuackApp) -> 'LEDLoopSettings':
        """
        Returns the settings page associated with this LED loop.
        """
        if not app:
            app = self.app
        else:
            assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        return LEDLoopSettings(app, self, uiFactory=self.settingUIFactory)

    def passArgs(self, leds: 'ws.PixelStrip', break_event: 'threading.Event'):
        """
        Passes the LED strip and break event to the loop.
        """
        self.leds = leds
        self.break_event = break_event

    def passApp(self, app: QuackApp):
        """
        Pass app args into the LED loop.
        This is used to access the app and navigator from within the loop.
        """
        assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        self.app = app
        self.after = app.after

    def checkBreak(self):
        """
        Checks if the break event is set.
        Returns True if the loop should stop, False otherwise.
        """
        if self.break_event.is_set():
            self.leds.show()
            return True
        return False

    def setFinished(self):
        self._isFinished = True

    def isFinished(self) -> bool:
        return self._isFinished

    def runInit(self):
        """
        Runs the initialization target function.
        """
        assert self.initTarget, "LEDLoop must have initTarget set before running."

        return self.initTarget(self)

    def runLoop(self):
        """
        Runs the LED loop with the provided target function.
        """
        assert self.leds, "LEDLoop must have leds set before running."
        assert self.break_event, "LEDLoop must have break_event set before running."
        assert self.after, "LEDLoop target requires after method to be set."

        return self.loopTarget(self)
