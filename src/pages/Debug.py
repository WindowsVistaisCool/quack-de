from typing import TYPE_CHECKING

from LEDThemes import LEDThemes
from pages.Home import HomePage
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
        ).grid(row=0, column=0, columnspan=10, padx=20, pady=20, sticky="nw")

        led_frame = (
            self.ui.add(
                ctk.CTkFrame,
                "led_frame",
            )
            .grid(row=1, column=0, columnspan=3, padx=20, pady=0, sticky="nsew")
            .getInstance()
        )

        self.ui.add(
            ctk.CTkButton,
            "nav_virtual",
            root=led_frame,
            text="View Virtual LEDs",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
            state="disabled",
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
            "freaky",
            root=led_frame,
            text="Freaky",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=2, padx=20, pady=10, sticky="nw")

        f_sock = (
            self.ui.add(
                ctk.CTkFrame,
                "socket_frame",
            )
            .grid(row=2, column=0, columnspan=10, padx=20, pady=20, sticky="nsew")
            .getInstance()
        )

        self.ui.add(
            ctk.CTkButton,
            "b_reconnect",
            root=f_sock,
            text="Reconnect",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=0, padx=20, pady=10, sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "b_dc",
            root=f_sock,
            text="Disconnect",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=1, padx=20, pady=10, sticky="n")

        self.ui.add(
            ctk.CTkButton,
            "b_kill",
            root=f_sock,
            text="Kill Server",
            height=50,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=2, padx=20, pady=10, sticky="ne")

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
                "WARNING! This is EPILEPSY mode which is DANGEROUS for the eyes!!! meow",
                lambda: self.appRoot.leds.setLoop(
                    LEDThemes.getTheme("epilepsy").id
                ),
                lambda: None,
            )
            self.navigator.navigateEphemeral(yndialog)

        self.ui.get("epilepsy").setCommand(epilepsy_call)
        self.ui.get("freaky").setCommand(
            lambda: self.appRoot.leds.setLoop(LEDThemes.getTheme("freaky").id)
        )

        self.ui.get("b_reconnect").setCommand(
            lambda: (
                self.appRoot.leds.begin(),
                self.navigator.navigate(HomePage),
            )
        )

        self.ui.get("b_dc").setCommand(
            lambda: (
                self.appRoot.leds.disconnect(),
                self.navigator.navigate(HomePage),
            )
        )

        self.ui.get("b_kill").setCommand(
            lambda: (
                self.appRoot.leds.killServer(),
                self.navigator.navigate(HomePage),
            )
        )
