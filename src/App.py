import customtkinter as ctk
import time
from datetime import datetime
from threading import Thread

from Configurator import Configurator
from LEDLoops import LEDLoops

from lib.CommandUI import CommandUI
from lib.DevChecks import isDev
from lib.Navigation import NavigationManager
from lib.Notifier import NotifierService, NotifierUI

from pages.Debug import DebugPage
from pages.LEDs import LEDsPage
from pages.Home import HomePage
from pages.Settings import SettingsPage

class App(ctk.CTk):
    VERSION = f"v0.1{'-dev' if isDev() else ''}"
    APP_TITLE = "QuackDE"
    APP_DESCRIPTION = "Quackings Dorm Environment\nWritten by Kyle Rush"
    FONT_NAME = "Ubuntu Mono"

    def __init__(self):
        Configurator.initialize(self.APP_TITLE)
        ctk.set_appearance_mode(Configurator.getInstance().getAppearanceMode())
        ctk.set_default_color_theme(Configurator.getInstance().getTheme())

        super().__init__()
        self.title(self.APP_TITLE)
        self.geometry("800x480")
        self.resizable(False, False)

        self.ui = CommandUI(self)

        NotifierService.setDelayFuncs(
            lambda delay_ms, end_call: self.after(delay_ms, end_call),
            self.after_cancel
        )
        NotifierService.init()
        NotifierUI.setFont((self.FONT_NAME, 16))

        self._fullAccessMode = False
        self._fullAccessTimerID = None
        self._fullAccessLockCallbacks = []

        self.content_root = self.ui.add(ctk.CTkFrame, "nav_root", fg_color=self._fg_color)
        self.navigation: 'NavigationManager' = NavigationManager(self.content_root.getInstance())
        self.navigation.registerExceptionHandling()

        self.leds = None

        self._initUI()
        self._initCommands()
        self._addPages()

    def setFullscreen(self, fullscreen: bool):
        _setter = lambda fs: self.attributes("-fullscreen", fs)
        self.bind("<Escape>", lambda e: _setter(False))
        _setter(fullscreen)
    
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
        self.navbar = self.ui.add(ctk.CTkFrame, "sb_main",
                              width=800,
                              corner_radius=0)
        self.navbar.grid(row=0, column=0, rowspan=10, sticky="nsew")
        self.navbar.getInstance().grid_rowconfigure(3, weight=1)

        self._fullAccessText = ctk.StringVar(value=f"{self.APP_TITLE}")
        self.ui.add(ctk.CTkLabel, "app_title",
                    root=self.navbar.getInstance(),
                    textvariable=self._fullAccessText,
                    font=(self.FONT_NAME, 28, "bold"),
                    ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="new")

        self.clock_label = ctk.StringVar(value="12:00 AM")
        self.ui.add(ctk.CTkLabel, "clock",
                    root=self.navbar.getInstance(),
                    textvariable=self.clock_label,
                    font=(self.FONT_NAME, 16),
                    ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="new")

        self.ui.add(ctk.CTkButton, "nav_home",
                    root=self.navbar.getInstance(),
                    text="Home", 
                    font=(self.FONT_NAME, 18),
                    width=150, height=60,
                    corner_radius=20
                    ).grid(row=2, column=0, padx=20, pady=(15, 0), sticky="new")

        self.ui.add(ctk.CTkButton, "nav_leds",
                    root=self.navbar.getInstance(),
                    text="LEDs",
                    font=(self.FONT_NAME, 18),
                    width=150, height=60,
                    corner_radius=20
                    ).grid(row=3, column=0, padx=20, pady=(15, 0), sticky="new")

        if isDev():
            self.ui.add(ctk.CTkButton, "nav_debug",
                        root=self.navbar.getInstance(),
                        text="Debug",
                        font=(self.FONT_NAME, 18),
                        width=150, height=60,
                        corner_radius=20
                        ).grid(row=4, column=0, padx=20, pady=(10, 0), sticky="sew")

        self.ui.add(ctk.CTkButton, "nav_settings", 
                    root=self.navbar.getInstance(),
                    text="Settings",
                    font=(self.FONT_NAME, 18),
                    width=150, height=60, 
                    corner_radius=20
                    ).grid(row=5, column=0, padx=20, pady=(10, 20), sticky="sew")
        
        self.notifierUI = CommandUI(self)
        self.notifierBase = self.notifierUI.add(ctk.CTkFrame, "notifier_base",
                                                fg_color="transparent",
                                                bg_color="transparent",
                                                ).withGridProperties(row=1, column=1, padx=0, pady=0, sticky="sew")
        self.notifierBase.getInstance().grid_columnconfigure(0, weight=1)
        self.notifierBase.getInstance().grid_rowconfigure(0, weight=1)
        self.notifierBase.grid()

        self.notifier = NotifierUI(self.notifierBase.getInstance(), self.notifierUI)
        NotifierService.setActiveUI(self.notifier)
        NotifierService.notify("", 100) # display a blank notification to initialize sizing properly

    def _initCommands(self):
        self.ui.addCommand("nav_home", lambda: self.navigation.navigate(HomePage))
        self.ui.addCommand("nav_leds", lambda: self.navigation.navigate(LEDsPage))
        if isDev():
            self.ui.addCommand("nav_debug", lambda: self.navigation.navigate(DebugPage))
        self.ui.addCommand("nav_settings", lambda: self.navigation.navigate(SettingsPage))

        # initilaze the clock
        self.clock_enabled = True
        def clock_worker():
            now = None
            while self.clock_enabled:
                now = datetime.now()
                self.clock_label.set(now.strftime("%I:%M:%S %p"))
                if now.minute % 60 == 0 and now.second == 0:
                    self.navigation.getPage(HomePage).updateGreeting(now)
                time.sleep(1)
        self.clock_thread = lambda: Thread(target=clock_worker, daemon=True)

    def _addPages(self):
        HomePage(self.navigation, self, self.content_root.getInstance())
        self.leds = LEDsPage(self.navigation, self, self.content_root.getInstance()).getLeds()
        DebugPage(self.navigation, self, self.content_root.getInstance())
        SettingsPage(self.navigation, self, self.content_root.getInstance())

        self.navigation.getPage(HomePage).updateGreeting(datetime.now())
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
            self._fullAccessTimerID = self.after((1 * 60 * 1000) if isDev() else (5 * 60 * 1000), self._disableFullAccessCallback)
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
            self._fullAccessTimerID = self.after(5 * 60 * 1000, self._disableFullAccessCallback)
        
    def addLockCallback(self, callback):
        """Adds a callback to be called when the lock is activated."""
        self._fullAccessLockCallbacks.append(callback)
        

if __name__ == "__main__":
    app = App()
    if not isDev():
        app.setFullscreen(True)
    app.toggleFullAccess(True)
    app.navigation.navigate(LEDsPage)
    app.leds.setLoop(LEDLoops.twinkle(app.after))
    app.mainloop()

