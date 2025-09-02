import multiprocessing
import threading
import copy
from typing import Callable
import rpi_ws281x as ws

from lib.Configurator import Configurator
from lib.QuackApp import QuackApp
from lib.led.LEDThemeSettings import LEDThemeSettings
from lib.led.WSExtensions import SegmentedPixelStrip, SubStrip


def _mpc_call_by_name(func_path: str, mpc_args):
    """Import and call a top-level function by its import path.

    This avoids trying to pickle a bound method or a lambda when spawning
    a new process (especially important on Windows where the spawn start
    method is used).
    """
    module_name, func_name = func_path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[func_name])
    func = getattr(mod, func_name)
    return func(mpc_args)


class LEDTheme:
    def __init__(
        self,
        id: str,
        loopTarget=lambda *_: 1,
        initTarget=lambda *_: None,
        settingsUIFactory: callable = None,
        *,
        allowMPC=False,
        imagePath: str = "assets/images/missing.png",
        friendlyName: str = None,
    ):
        self.id = id
        self._loopTarget = loopTarget
        self._initTarget = initTarget
        self.settingUIFactory = settingsUIFactory
        self.allowMPC = allowMPC
        self.imagePath = imagePath
        self.friendlyName = friendlyName or self.id

        self.themeData = Configurator.getInstance().get(self.id, {})

        self.app: "QuackApp" = None

        self.leds: "SegmentedPixelStrip" = None
        self.strip: "SubStrip" = None

        self.break_event: "threading.Event" = None
        self.after = lambda delay, callback: None

    def getSettings(self, app: QuackApp) -> "LEDThemeSettings":
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

    def saveData(self, data: dict = None):
        if not data:
            data = self.getData()
        Configurator.getInstance().set(self.id, data)
        Configurator.getInstance().saveSettings()

    def passArgs(
        self, leds: "ws.PixelStrip", break_event: "threading.Event", subStrip=None
    ):
        """
        Passes the LED strip and break event to the loop.
        """
        self.leds = leds
        self.strip = (
            self.leds.getSubStrip(subStrip) if subStrip is not None else self.leds
        )
        self.break_event = break_event

    def passApp(self, app: QuackApp):
        """
        Pass app args into the LED loop.
        This is used to access the app and navigator from within the loop.
        """
        assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        self.app = app
        self.after = app.after

    def passAfter(self, call):
        self.after = call

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

        if self.allowMPC:
            self.after = lambda delay, callback: None
            self.mpcArgs = MPCTargetParams(self.strip, self.checkBreak)

        return self._initTarget(self)

    def runLoop(self):
        """
        Runs the LED loop with the provided target function.
        """
        assert self.leds, "LEDLoop must have leds set before running."
        assert self.break_event, "LEDLoop must have break_event set before running."
        # assert self.after, "LEDLoop target requires after method to be set."

        return self._loopTarget(self)

    def getLoopTargetMPC(self):
        """Return a callable that starts the loop target in a separate process.

        Requirements / notes:
        - The loop target must be a top-level (module-level) function (not a
            lambda or nested function). That function will be imported in the
            child process by name so it doesn't need to be pickled.
        - The data placed into `MPCTargetParams` (self.mpcArgs) must be
            picklable. In particular, hardware objects (like ws.PixelStrip
            instances) cannot be pickled. Instead pass lightweight config or
            identifiers and re-open hardware from the child process if needed.
        """
        assert self.allowMPC, "LEDLoop must have allowMPC set to True to use MPC."

        func = self._loopTarget

        # Reject inner functions and lambdas which can't be reliably imported
        qual = getattr(func, "__qualname__", "")
        if "<locals>" in qual or (not hasattr(func, "__name__")):
            raise ValueError(
                "loopTarget must be a top-level (module-level) function to run in a separate process"
            )

        func_path = f"{func.__module__}.{func.__name__}"
        copyArgs = copy.deepcopy(self.mpcArgs)

        def _starter():
            # Start a new process that imports the function by name and calls it
            p = multiprocessing.Process(target=_mpc_call_by_name, args=(func_path, copyArgs))
            p.start()
            return p

        return _starter


class MPCTargetParams:
    def __init__(self, strip, checkBreak):
        self.strip: "SegmentedPixelStrip" = strip
        self.checkBreak: "Callable" = checkBreak
