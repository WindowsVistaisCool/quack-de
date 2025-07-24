from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage

class HomePage(NavigationPage):
    def __init__(self, appRoot: 'App', master, **kwargs):
        super().__init__(master, title="Home", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text="🏠 Home",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=30, pady=30, sticky="nw")

    def _initCommands(self):
        pass