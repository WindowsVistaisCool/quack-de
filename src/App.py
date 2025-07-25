import customtkinter as ctk
import time
from datetime import datetime
from threading import Thread

from Configurator import Configurator

from lib.CommandUI import CommandUI
from lib.DevChecks import isDev
# isDev = lambda: True
from lib.Navigation import NavigationManager
from lib.Notifier import NotifierService, NotifierUI

from pages.Debug import DebugPage
from pages.Home import HomePage
from pages.Settings import SettingsPage

class App(ctk.CTk):
    VERSION = f"0.1{'-dev' if isDev() else ''}"
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

        self.content_root = self.ui.add(ctk.CTkFrame, "nav_root", fg_color=self._fg_color)
        self.navigation: 'NavigationManager' = NavigationManager(self.content_root.getInstance())
        self.navigation.registerExceptionHandling()

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

        self.ui.add(ctk.CTkLabel, "app_title",
                    root=self.navbar.getInstance(),
                    text=self.APP_TITLE,
                    font=(self.FONT_NAME, 28, "bold"),
                    ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="new")

        self.clock_label = ctk.StringVar(value="12:00 AM")
        self.ui.add(ctk.CTkLabel, "clock",
                    root=self.navbar.getInstance(),
                    textvariable=self.clock_label,
                    font=(self.FONT_NAME, 16),
                    ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="new")

        self.ui.add(ctk.CTkButton, "nav_home",
                    root=self.navbar.getInstance(),
                    text="Home", 
                    font=(self.FONT_NAME, 18),
                    width=150, height=50,
                    corner_radius=12
                    ).grid(row=2, column=0, padx=30, pady=10, sticky="new")

        if isDev():
            self.ui.add(ctk.CTkButton, "nav_debug",
                        root=self.navbar.getInstance(),
                        text="Debug",
                        font=(self.FONT_NAME, 18),
                        width=150, height=50,
                        corner_radius=12
                        ).grid(row=3, column=0, padx=30, pady=10, sticky="new")

        self.ui.add(ctk.CTkButton, "nav_settings", 
                    root=self.navbar.getInstance(),
                    text="Settings",
                    font=(self.FONT_NAME, 18),
                    width=150, height=50, 
                    corner_radius=12
                    ).grid(row=4, column=0, padx=30, pady=40, sticky="s")
        
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
        if isDev():
            self.ui.addCommand("nav_debug", lambda: self.navigation.navigate(DebugPage))
        self.ui.addCommand("nav_settings", lambda: self.navigation.navigate(SettingsPage))

        # initilaze the clock
        self.clock_enabled = True
        def clock_worker():
            while self.clock_enabled:
                self.clock_label.set(datetime.now().strftime("%I:%M:%S %p"))
                time.sleep(1)
        self.clock_thread = lambda: Thread(target=clock_worker, daemon=True)
        self.clock_thread().start()

    def _addPages(self):
        HomePage(self.navigation, self, self.content_root.getInstance())
        DebugPage(self.navigation, self, self.content_root.getInstance())
        SettingsPage(self.navigation, self, self.content_root.getInstance())

        self.navigation.navigate(HomePage)

    def toggleNav(self, viewable):
        if not viewable:
            self.navbar.drop()
        else:
            self.navbar.grid()

if __name__ == "__main__":
    app = App()
    # if not isDev():
    #     app.setFullscreen(True)
    app.mainloop()

