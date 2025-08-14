import threading
import rpi_ws281x as ws

from lib.Configurator import Configurator
from lib.QuackApp import QuackApp
from lib.led.LEDThemeSettings import LEDThemeSettings
from lib.led.WSExtensions import SegmentedPixelStrip, SubStrip

class LEDTheme:
    def __init__(self,
            id: str,
            loopTarget=lambda *_: 1,
            initTarget=lambda *_: None,
            settingsUIFactory: callable = None,
            *,
            imagePath: str = "assets/images/missing.png",
            friendlyName: str = None,
            stripID = None,
        ):
        self.id = id
        self._loopTarget = loopTarget
        self._initTarget = initTarget
        self.settingUIFactory = settingsUIFactory
        self.imagePath = imagePath
        self.friendlyName = friendlyName or self.id
        self.stripID = stripID

        self.themeData = Configurator.getInstance().get(self.id, {})

        self.app: 'QuackApp' = None

        self.leds: 'SegmentedPixelStrip' = None
        self.strip: 'SubStrip' = None

        self.break_event: 'threading.Event' = None
        self.after = lambda delay, callback: None

    def setStripID(self, id: int):
        self.stripID = id

    def getSettings(self, app: QuackApp) -> 'LEDThemeSettings':
        """
        Returns the settings page associated with this LED loop.
        """
        if not app:
            app = self.app
        else:
            assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        return LEDThemeSettings(app, self, uiFactory=self.settingUIFactory)
    
    def getData(self) -> dict:
        return self.themeData

    def setData(self, key, value):
        """
        Sets a value in the LED theme data.
        """
        self.themeData[key] = value

    def saveData(self, data: dict=None):
        if not data:
            data = self.getData()
        Configurator.getInstance().set(self.id, data)
        Configurator.getInstance().saveSettings()

    def passArgs(self, leds: 'ws.PixelStrip', break_event: 'threading.Event'):
        """
        Passes the LED strip and break event to the loop.
        """
        self.leds = leds
        self.strip = self.leds.getSubStrip(self.stripID) if self.stripID is not None else self.leds
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

    def runInit(self):
        """
        Runs the initialization target function.
        """
        assert self._initTarget, "LEDLoop must have initTarget set before running."

        return self._initTarget(self)

    def runLoop(self):
        """
        Runs the LED loop with the provided target function.
        """
        assert self.leds, "LEDLoop must have leds set before running."
        assert self.break_event, "LEDLoop must have break_event set before running."
        assert self.after, "LEDLoop target requires after method to be set."

        return self._loopTarget(self)
