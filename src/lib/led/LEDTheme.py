import threading
import rpi_ws281x as ws

from lib.QuackApp import QuackApp
from lib.led.LEDThemeSettings import LEDThemeSettings

class LEDTheme:
    def __init__(self,
                 id: str, loopTarget=lambda *_: 1,
                 initTarget=lambda *_: None,
                 settingsUIFactory: callable = None,
                 *,
                 imagePath: str = "assets/images/missing.png",
                 friendlyName: str = None,
                ):
        self.id = id
        self.friendlyName = friendlyName or self.id

        self.imagePath = imagePath

        self.loopTarget = loopTarget
        self.initTarget = initTarget

        self.settingUIFactory = settingsUIFactory

        self.app: 'QuackApp' = None

        self._disableSafetySleep = False

        self.leds: 'ws.PixelStrip' = None
        self.break_event: 'threading.Event' = None
        self.after = lambda delay, callback: None

    def getSettings(self, app: QuackApp) -> 'LEDThemeSettings':
        """
        Returns the settings page associated with this LED loop.
        """
        if not app:
            app = self.app
        else:
            assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        return LEDThemeSettings(app, self, uiFactory=self.settingUIFactory)

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
