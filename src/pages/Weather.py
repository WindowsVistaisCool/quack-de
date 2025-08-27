from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage


class WeatherPage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Weather", **kwargs)
        self.appRoot: "App" = appRoot

        self._initUI()
        self._initCommands()
    
    def _initUI(self):
        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="Weather",
            font=(self.appRoot.FONT_NAME, 32, "bold")
        ).grid(row=0, column=0, columnspan=10, padx=30, pady=(35, 25), sticky="nw")

        

    def _initCommands(self):
        pass
