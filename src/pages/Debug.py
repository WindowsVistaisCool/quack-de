from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage

from pages.Home import HomePage

class DebugPage(NavigationPage):
    def __init__(self, appRoot: 'App', master, **kwargs):
        super().__init__(master, title="Debug", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text="hehehaw this is the debug page!!!! grrrr",
                    font=(self.appRoot.FONT_NAME, 24)
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "destroy",
                    text="destroy everything!! har har har",
                    ).grid(row=1, column=0, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "rebuild",
                    text="magical fix everything button!!! har har harhahrarhraR!!!!!!",
                    ).grid(row=2, column=0, padx=20, pady=20, sticky="nw")
    
    def _initCommands(self):
        self.ui.addCommand("destroy", self.appRoot.navbar.instance.grid_forget)

        def funny():
            self.appRoot.ui.gridAll()
            if self.appRoot.navigation.pageExists(HomePage):
                self.appRoot.navigation.navigate(HomePage)

        self.ui.addCommand("rebuild", funny)
        # Add more commands as needed for debugging purposes
        # e.g., self.ui.addCommand("some_command", lambda: some_function())