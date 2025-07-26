from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage

class HomePage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Home", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text="🏠 Home",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkLabel, "description",
                    text=f"Since there are no modules, here is your quote of the day:\n thank you for using {self.appRoot.APP_TITLE}",
                    font=(self.appRoot.FONT_NAME, 16),
                    justify="center"
                    ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def _initCommands(self):
        pass