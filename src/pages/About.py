from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import platform
from lib.Navigation import NavigationPage
from lib.Notifier import NotifierUI

class AboutPage(NavigationPage):
    ABOUT_TEXT = """This is a custom application built with Python and CustomTkinter.
Made by Kyle Rush.
"""

    PLATFORM_TEXT = f"""OS: {platform.platform()}
Architecture: {platform.architecture()[0]}
Python Version: {platform.python_version()}
"""

    def __init__(self, appRoot: 'App', master, **kwargs):
        super().__init__(master, title="About", **kwargs)
        self.appRoot: 'App' = appRoot

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure((0), weight=1)

        self.ui.add(ctk.CTkLabel, "title",
                    text=f"💡 About {self.appRoot.APP_TITLE}",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=30, pady=30, sticky="nw")

        self.ui.add(ctk.CTkLabel, "description",
                    text=self.ABOUT_TEXT,
                    font=(self.appRoot.FONT_NAME, 16)
                    ).grid(row=1, column=0, padx=30, pady=10, sticky="nwe")

    
        f_version = self.ui.add(ctk.CTkFrame, "f_version",
                    width=400, height=50,
                    ).withGridProperties(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_version.getInstance().grid_columnconfigure(0, weight=1)
        f_version.grid()

        self.ui.add(ctk.CTkLabel, "l_version",
                    root=f_version.getInstance(),
                    text=f"App Version: {self.appRoot.VERSION}",
                    font=(self.appRoot.FONT_NAME, 14)
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")

        f_specs = self.ui.add(ctk.CTkFrame, "f_specs",
                    width=400, height=50,
                    ).withGridProperties(row=3, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_specs.getInstance().grid_columnconfigure(0, weight=1)
        f_specs.grid()

        self.ui.add(ctk.CTkLabel, "l_specs",
                    root=f_specs.getInstance(),
                    text="Hardware Specifications:",
                    font=(self.appRoot.FONT_NAME, 16, "bold")
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")
    
        self.ui.add(ctk.CTkLabel, "l_specs_pc",
                    root=f_specs.getInstance(),
                    text=self.PLATFORM_TEXT,
                    font=(self.appRoot.FONT_NAME, 14),
                    justify="left"
                    ).grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsw")

        self.ui.add(ctk.CTkButton, "nav_back",
                    text="Back",
                    font=(self.appRoot.FONT_NAME, 18),
                    width=150, height=50,
                    corner_radius=12
                    ).grid(row=4, column=0, padx=30, pady=20, sticky="s")
    
    def _initCommands(self):
        self.ui.addCommand("nav_back", lambda: self.appRoot.navigation.navigate(type(self.appRoot.navigation.previousPage)))

    def onShow(self):
        self.appRoot.toggleNav(False)
    
    def onHide(self):
        self.appRoot.toggleNav(True)
        pass