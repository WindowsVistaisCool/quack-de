from typing import Type
import customtkinter as ctk
import threading
import rpi_ws281x as ws

from lib.CommandUI import CommandUI
from lib.Navigation import EphemeralNavigationPage, NavigationManager
from lib.QuackApp import QuackApp
from lib.led.LEDLoopSettings import LEDLoopSettings

class LEDLoop:
    def __init__(self, id: str, loopTarget=lambda *_: 1, initTarget=lambda *_: None, settingsUIFactory: callable = None):
        self.id = id

        # self._isFinished = False

        self.loopTarget = loopTarget
        self.initTarget = initTarget

        self.settingUIFactory = settingsUIFactory

        self.app: 'QuackApp' = None
        self.navigator: NavigationManager = None

        self.leds: 'ws.PixelStrip' = None
        self.break_event: 'threading.Event' = None
        self.after = lambda delay, callback: None

    def getSettings(self, app: QuackApp) -> 'LEDLoopSettings':
        """
        Returns the settings page associated with this LED loop.
        """
        assert self.settingUIFactory, "LEDLoop must have settingsUIFactory set before accessing settings."
        if not self.navigator and not app:
            raise RuntimeError("LEDLoop must have navigator set before accessing settings.")
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

    def passApp(self, app: QuackApp, navigator: 'NavigationManager'):
        """
        Pass app args into the LED loop.
        This is used to access the app and navigator from within the loop.
        """
        assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        assert isinstance(navigator, NavigationManager), "navigator must be an instance of NavigationManager"
        self.app = app
        self.after = app.after
        self.navigator = navigator

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
