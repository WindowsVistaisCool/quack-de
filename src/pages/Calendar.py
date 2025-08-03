from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage


class CalendarPage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Calendar", **kwargs)
        self.appRoot: "App" = appRoot

        self._initUI()
        self._initCommands()
    
    def _initUI(self):
        pass

    def _initCommands(self):
        pass
