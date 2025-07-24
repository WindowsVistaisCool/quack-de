from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Configurator import Configurator
from lib.Dialogs import Dialogs
from lib.Navigation import NavigationPage
from lib.Notifier import NotifierService
from lib.Themes import Theme

from pages.About import AboutPage

class SettingsPage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Settings", **kwargs)
        self.appRoot: 'App' = appRoot

        self.hasUnsavedChanges = False

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

        f_settings = self.ui.add(ctk.CTkFrame, "f_settings",
                    width=400, height=50,
                    ).withGridProperties(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_settings.getInstance().grid_columnconfigure(1, weight=1)
        f_settings.grid()

        self.ui.add(ctk.CTkLabel, "l_theme",
                    root=f_settings.getInstance(),
                    text="Theme settings:",
                    font=(self.appRoot.FONT_NAME, 14, "bold")
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")

        self.om_theme = ctk.StringVar(value=Theme(Configurator.getInstance().getTheme()).name)
        self.ui.add(ctk.CTkOptionMenu, "om_theme",
                    root=f_settings.getInstance(),
                    variable=self.om_theme,
                    values=Theme.getThemeNames(),
                    ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="sw")

        self.s_darkmode = ctk.BooleanVar(value=Configurator.getInstance().getAppearanceMode() == "dark")
        s_darkmode = self.ui.add(ctk.CTkSwitch, "s_darkmode",
                    root=f_settings.getInstance(),
                    text="Dark Mode",
                    variable=self.s_darkmode,
                    ).withGridProperties(row=1, column=1, padx=20, pady=(0, 10), sticky="se")
        if self.s_darkmode.get() == "dark":
            s_darkmode.getInstance().toggle()
        s_darkmode.grid()

        self.b_save = self.ui.add(ctk.CTkButton, "save",
                    text="Save Settings",
                    height=40,
                    font=(self.appRoot.FONT_NAME, 16),
                    corner_radius=12
                    ).withGridProperties(row=3, column=0, columnspan=2, padx=30, pady=(20, 10), sticky="se")

    def _initCommands(self):
        self.ui.get("about").setCommand(lambda: self.appRoot.navigation.navigate(AboutPage))

        def hasUnsaved():
            self.hasUnsavedChanges = True
            self.ui.get("save").grid()

        def om_callback(result: str):
            hasUnsaved()
            if result == Theme(Configurator.getInstance().getTheme()).name:
                return
            Configurator.getInstance().setTheme(Theme[result])
            NotifierService.notify(f"You must restart for these changes to take effect!", 4000)

        self.ui.get("om_theme").setCommand(om_callback)
        self.ui.get("s_darkmode").setCommand(hasUnsaved)

        def save_invoke():
            self.ui.get("save").drop()

            Configurator.getInstance().setAppearanceMode("dark" if self.s_darkmode.get() else "light")
            Configurator.getInstance().saveSettings()
            NotifierService.notify("Settings saved successfully!", 1500)

            ctk.set_appearance_mode(Configurator.getInstance().getAppearanceMode())

        self.ui.get("save").setCommand(save_invoke)
