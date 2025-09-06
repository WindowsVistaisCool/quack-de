import traceback
import customtkinter as ctk
import os
import time
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

from API import QuackDEAPI
from LEDThemes import LEDThemes

from lib.Configurator import Configurator
from lib.CommandUI import CommandUI
from lib.DevChecks import isDev
from lib.Notifier import NotifierService, NotifierUI
from lib.QuackApp import QuackApp

from lib.led.SocketLED import SocketLED
from pages.Calendar import CalendarPage
from pages.Debug import DebugPage
from pages.LEDs import LEDsPage
from pages.Home import HomePage
from pages.Settings import SettingsPage
from pages.Weather import WeatherPage

if os.name != "nt":
    import psutil

    def cpuPercent():
        return psutil.cpu_percent()

    def cpuTemp():
        return int(psutil.sensors_temperatures().get("cpu_thermal", [])[0].current)
else:
    def cpuPercent():
        return 67

    def cpuTemp():
        return 67 # he he he haw

class App(QuackApp):
    VERSION = f"v2.0{'-dev' if isDev() else ''}"
    APP_TITLE = "QuackDE"
    APP_DESCRIPTION = "Quackings Dorm Environment\nWritten by Kyle Rush"
    FONT_NAME = "Ubuntu Mono"

    def __init__(self):
        load_dotenv()
        Configurator.setSchemaVersion(2)

        super().__init__(appTitle=self.APP_TITLE)
        self.geometry("800x480")
        self.resizable(False, False)

        NotifierUI.setFont((self.FONT_NAME, 16))

        self._fullAccessMode = False
        self._fullAccessTimerID = None
        self._fullAccessLockCallbacks = []

        self.leds = SocketLED()
        LEDThemes() # initialize themes

        self._initUI()
        self._initCommands()
        self._addPages()

        self.api = QuackDEAPI(self.leds)
        if not isDev():
            self.api.init()

    def _initUI(self):
        # init grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # grid in the nav root
        self.content_root.grid(row=0, column=1, sticky="nsew")
        self.content_root.getInstance().grid_rowconfigure(0, weight=1)
        self.content_root.getInstance().grid_columnconfigure(0, weight=1)

        # init nav sidebar
        self.navbar = self.ui.add(ctk.CTkFrame, "sb_main", width=800, corner_radius=0)
        self.navbar.grid(row=0, column=0, rowspan=10, sticky="nsew")
        self.navbar.getInstance().grid_rowconfigure((7), weight=1)

        self._fullAccessText = ctk.StringVar(value=f"{self.APP_TITLE}")
        self.ui.add(
            ctk.CTkLabel,
            "app_title",
            root=self.navbar.getInstance(),
            textvariable=self._fullAccessText,
            font=(self.FONT_NAME, 28, "bold"),
            pady=0,
        ).grid(row=0, column=0, padx=20, pady=(20, 0), sticky="new")

        self.clock_label = ctk.StringVar(value="Unknown Time")
        self.ui.add(
            ctk.CTkLabel,
            "clock",
            root=self.navbar.getInstance(),
            textvariable=self.clock_label,
            font=(self.FONT_NAME, 16),
        ).grid(row=1, column=0, padx=20, pady=(5, 0), sticky="new")

        self.temp_label = ctk.StringVar(value="CPU: ?% ?°C")
        self.ui.add(
            ctk.CTkLabel,
            "temp",
            root=self.navbar.getInstance(),
            textvariable=self.temp_label,
            font=(self.FONT_NAME, 16),
            pady=0,
        ).grid(row=2, column=0, padx=20, pady=(0, 0), sticky="new")

        self.ui.add(
            ctk.CTkButton,
            "nav_home",
            root=self.navbar.getInstance(),
            text="Home",
            font=(self.FONT_NAME, 18),
            width=150,
            height=60,
            corner_radius=20,
        ).grid(row=3, column=0, padx=20, pady=(10, 0), sticky="new")

        self.ui.add(
            ctk.CTkButton,
            "nav_leds",
            root=self.navbar.getInstance(),
            text="LEDs",
            font=(self.FONT_NAME, 18),
            width=150,
            height=60,
            corner_radius=20,
        ).grid(row=4, column=0, padx=20, pady=(10, 0), sticky="new")

        self.ui.add(
            ctk.CTkButton,
            "nav_weather",
            root=self.navbar.getInstance(),
            text="Weather",
            font=(self.FONT_NAME, 18),
            width=150,
            height=60,
            corner_radius=20,
        ).grid(row=5, column=0, padx=20, pady=(10, 0), sticky="new")

        self.ui.add(
            ctk.CTkButton,
            "nav_debug",
            root=self.navbar.getInstance(),
            text="Secrets",
            font=(self.FONT_NAME, 18),
            width=140,
            height=40,
            corner_radius=20,
        ).withGridProperties(row=6, column=0, padx=20, pady=(10, 0), sticky="s")

        self.ui.add(
            ctk.CTkButton,
            "nav_settings",
            root=self.navbar.getInstance(),
            text="Settings",
            font=(self.FONT_NAME, 18),
            width=140,
            height=50,
            corner_radius=20,
        ).grid(row=7, column=0, padx=20, pady=(10, 15), sticky="s")

        # TODO: move this to QuackApp
        self.notifierUI = CommandUI(self)
        self.notifierBase = self.notifierUI.add(
            ctk.CTkFrame,
            "notifier_base",
            fg_color="transparent",
            bg_color="transparent",
        ).withGridProperties(row=1, column=1, padx=0, pady=0, sticky="sew")
        self.notifierBase.getInstance().grid_columnconfigure(0, weight=1)
        self.notifierBase.getInstance().grid_rowconfigure(0, weight=1)
        self.notifierBase.grid()

        self.notifier = NotifierUI(self.notifierBase.getInstance(), self.notifierUI)
        NotifierService.setActiveUI(self.notifier)
        NotifierService.notify(
            "", 100
        )  # display a blank notification to initialize sizing properly

    def _initCommands(self):
        self.ui.addCommand("nav_home", lambda: self.navigation.navigate(HomePage))
        self.ui.addCommand("nav_leds", lambda: self.navigation.navigate(LEDsPage))
        self.ui.addCommand("nav_weather", lambda: self.navigation.navigate(WeatherPage))
        self.ui.addCommand("nav_debug", lambda: self.navigation.navigate(DebugPage))
        self.ui.addCommand(
            "nav_settings", lambda: self.navigation.navigate(SettingsPage)
        )

        # initialize the clock
        self.clock_enabled = True

        def clock_worker():
            now = datetime.now()

            def update():
                self.navigation.getPage(HomePage).updateGreeting(now)
                self.navigation.getPage(WeatherPage).updateTime(now)

            update()
            while self.clock_enabled:
                now = datetime.now()
                self.clock_label.set(now.strftime("%I:%M:%S %p"))
                self.temp_label.set(f"CPU: {cpuPercent()}% {cpuTemp()}°C")
                if now.minute % 60 == 0 and now.second == 0:
                    update()
                time.sleep(1)

        self.clock_thread = lambda: Thread(target=clock_worker, daemon=True)

        self.addLockCallback(lambda: self.ui.get("nav_debug").drop())

    def _addPages(self):
        LEDsPage(self.navigation, self, self.content_root.getInstance())
        WeatherPage(self.navigation, self, self.content_root.getInstance())
        DebugPage(self.navigation, self, self.content_root.getInstance())
        SettingsPage(self.navigation, self, self.content_root.getInstance())
        HomePage(self.navigation, self, self.content_root.getInstance())

        self.clock_thread().start()

        self.navigation.navigate(HomePage)

        

    def toggleNav(self, viewable):
        if not viewable:
            self.navbar.drop()
        else:
            self.navbar.grid()

    def _disableFullAccessCallback(self):
        """Callback to disable full access mode."""
        self.toggleFullAccess(False)
        [call() for call in self._fullAccessLockCallbacks]

    def toggleFullAccess(self, enable: bool):
        """Enables or disables full access mode, which allows access to all pages."""
        self._fullAccessMode = enable
        if enable:
            self._fullAccessText.set(f"🔓 {self.APP_TITLE}")
            self.ui.get("nav_debug").grid()
            self._fullAccessTimerID = self.after(
                5 * 60 * 1000,
                self._disableFullAccessCallback,
            )
        elif not enable and self._fullAccessTimerID is not None:
            self.after_cancel(self._fullAccessTimerID)
            [call() for call in self._fullAccessLockCallbacks]
            self._fullAccessText.set(f"{self.APP_TITLE}")
            self._fullAccessTimerID = None

    def hasFullAccess(self) -> bool:
        """Returns whether full access mode is enabled."""
        return self._fullAccessMode

    def resetFullAccessTimer(self):
        """Resets the full access timer, if it is running."""
        if self._fullAccessTimerID is not None:
            self.after_cancel(self._fullAccessTimerID)
            self._fullAccessTimerID = self.after(
                5 * 60 * 1000, self._disableFullAccessCallback
            )

    def addLockCallback(self, callback):
        """Adds a callback to be called when the lock is activated."""
        self._fullAccessLockCallbacks.append(callback)


if __name__ == "__main__":
    app = App()
    if not isDev():
        app.setFullscreen(True)
    else:
        app.toggleFullAccess(True)

    # self.appRoot.setLoop(LEDThemes.getTheme("twinkle"), subStrip="All")
    

    dev = isDev()
    try:
        app.mainloop()
    except:
        if dev:
            ts = datetime.now().timestamp()
            os.system(f"touch {os.path.expanduser(f'~/{ts}')}")
            with open(os.path.expanduser(f"~/{ts}.log"), "w") as f:
                f.write(traceback.format_exc())
