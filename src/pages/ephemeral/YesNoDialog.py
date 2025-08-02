from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import EphemeralNavigationPage


class YesNoDialog(EphemeralNavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Confirm", **kwargs)
        self.appRoot: "App" = appRoot

        self.yesCallback = None
        self.noCallback = None

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "message",
            text="Are you sure you want to proceed?",
            font=(self.appRoot.FONT_NAME, 20),
            justify="center",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="sew")

        self.ui.add(
            ctk.CTkButton,
            "yes",
            text="Yes",
            height=40,
            font=(self.appRoot.FONT_NAME, 20),
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ne")

        self.ui.add(
            ctk.CTkButton, "no", text="No", height=40, font=(self.appRoot.FONT_NAME, 20)
        ).grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nw")

    def _initCommands(self):
        self.ui.get("yes").setCommand(self.yesCallback)
        self.ui.get("no").setCommand(self.noCallback)

    def init(self, message: str, yesCallback=None, noCallback=None):
        """Configures the dialog with a message."""
        self.ui.get("message").getInstance().configure(text=message)

        def wrapYes():
            self.navigator.navigateBack()
            if yesCallback:
                yesCallback()

        def wrapNo():
            self.navigator.navigateBack()
            if noCallback:
                noCallback()

        self.yesCallback = wrapYes
        self.noCallback = wrapNo
        self._initCommands()
