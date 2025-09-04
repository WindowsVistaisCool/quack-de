from typing import TYPE_CHECKING

from LEDService import LEDService
from LEDThemes import LEDThemes
from pages.VirtualLED import VirtualLEDs
from pages.ephemeral.YesNoDialog import YesNoDialog

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage


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
            text="🤫 Secret Page",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        led_frame = (
            self.ui.add(
                ctk.CTkFrame,
                "led_frame",
            )
            .grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
            .getInstance()
        )

        self.ui.add(
            ctk.CTkButton,
            "nav_virtual",
            root=led_frame,
            text="View Virtual LEDs",
            height=50,
            font=(self.appRoot.FONT_NAME, 18, "bold"),
        ).grid(row=0, column=0, padx=20, pady=10, sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "epilepsy",
            root=led_frame,
            text="Epilepsy Theme",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=1, padx=20, pady=10, sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "debug",
            text="send sig",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=2, column=0, padx=20, pady=10, sticky="nw")

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

        def epilepsy_call():
            yndialog = YesNoDialog(
                self.navigator,
                self.appRoot,
                self.appRoot.content_root.getInstance(),
            )
            yndialog.init(
                "WARNING! This is EPILEPSY mode which is inherently DANGEROUS for the eyes!!!",
                lambda: LEDService.getInstance().setLoop(LEDThemes.getTheme("epilepsy")),
                lambda: None,
            )
            self.navigator.navigateEphemeral(yndialog)

        self.ui.get("epilepsy").setCommand(epilepsy_call)

        self.ui.get("debug").setCommand(
            lambda: (
                LEDService.getInstance().leds.setLoop("rainbow"),
            )
        )
