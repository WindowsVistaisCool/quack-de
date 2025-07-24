from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Configurator import Configurator
from lib.Dialogs import Dialogs
from lib.Navigation import NavigationPage
from lib.Notifier import NotifierUI
from lib.Themes import Theme

from pages.About import AboutPage

class SettingsPage(NavigationPage):
    def __init__(self, appRoot: 'App', master, **kwargs):
        super().__init__(master, title="Settings", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)

        self.ui.add(ctk.CTkLabel, "title",
                    text="⚙️ Settings",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=30, pady=30, sticky="nw")
    
        self.ui.add(ctk.CTkButton, "about",
                    text=f"About {self.appRoot.APP_TITLE}",
                    font=(self.appRoot.FONT_NAME, 18),
                    width=100, height=40,
                    corner_radius=12
                    ).grid(row=0, column=1, padx=30, pady=30, sticky="ne")

        self.ui.add(ctk.CTkLabel, "l_desc",
                    text="Configure application settings here",
                    font=(self.appRoot.FONT_NAME, 16)
                    ).grid(row=1, column=0, padx=30, pady=5, sticky="nw")

        f_theme = self.ui.add(ctk.CTkFrame, "f_theme",
                    width=400, height=50,
                    ).withGridProperties(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_theme.getInstance().grid_columnconfigure(1, weight=1)
        f_theme.grid()

        self.ui.add(ctk.CTkLabel, "l_theme",
                    root=f_theme.getInstance(),
                    text="Theme (Must restart to apply):",
                    font=(self.appRoot.FONT_NAME, 14, "bold")
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")

        self.om_theme = ctk.StringVar(value=Configurator.getInstance().getTheme().name)
        self.ui.add(ctk.CTkOptionMenu, "om_theme",
                    root=f_theme.getInstance(),
                    variable=self.om_theme,
                    values=Theme.getThemeNames(),
                    ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="sw")

        self.s_darkmode = ctk.BooleanVar(value=ctk.get_appearance_mode() == "dark")
        s_darkmode = self.ui.add(ctk.CTkSwitch, "s_darkmode",
                    root=f_theme.getInstance(),
                    text="Dark Mode",
                    variable=self.s_darkmode,
                    ).withGridProperties(row=1, column=1, padx=20, pady=(0, 10), sticky="se")
        s_darkmode.getInstance().toggle()
        s_darkmode.grid()

    def _initCommands(self):
        self.ui.get("about").setCommand(lambda: self.appRoot.navigation.navigate(AboutPage))

        def notifier(result: str):
            if result == Configurator.getInstance().getTheme().name:
                return
            Configurator.getInstance().setTheme(Theme[result])
            NotifierUI.notify(f"You must restart for these changes to take effect!", 4000)

        self.ui.get("om_theme").setCommand(notifier)
        self.ui.get("s_darkmode").setCommand(lambda: ctk.set_appearance_mode("light" if not self.s_darkmode.get() else "dark"))
