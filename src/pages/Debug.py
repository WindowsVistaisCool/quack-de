from typing import TYPE_CHECKING

from pages.VirtualLED import VirtualLEDs

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage
from lib.Notifier import NotifierService


class DebugPage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Debug", **kwargs)
        self.appRoot: "App" = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="hehehaw this is the debug page!!!! grrrr",
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=0, column=0, columnspan=10, padx=20, pady=20, sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "nav_virtual",
            text="Virtual LEDs",
        ).grid(row=1, column=0, padx=20, pady=0, sticky="nw")

    def _initCommands(self):
        self.ui.get("nav_virtual").setCommand(
            lambda: self.navigator.navigateEphemeral(
                VirtualLEDs(
                    self.navigator,
                    self.appRoot,
                    self.appRoot.content_root.getInstance(),
                )
            )
        )
