from typing import TYPE_CHECKING

from LEDService import LEDService
from pages.ephemeral.StatImg import StatImg
from PIL import Image


if TYPE_CHECKING:
    from App import App

import customtkinter as ctk

from lib.Navigation import NavigationPage


class HomePage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Home", **kwargs)
        self.appRoot: "App" = appRoot

        self.greetingText = ctk.StringVar(value=f"🏠 Home")

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(
            ctk.CTkLabel,
            "title",
            textvariable=self.greetingText,
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, columnspan=10, padx=30, pady=(35, 25), sticky="nw")

        self.ui.add(
            ctk.CTkLabel,
            "l_quickact",
            text="Quick Actions",
            font=(self.appRoot.FONT_NAME, 26),
        ).grid(row=1, column=0, padx=30, pady=(0, 15), sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "b_ledoff",
            text="Turn LEDs Off",
            border_spacing=12,
            corner_radius=12,
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=2, column=0, padx=30, pady=(0, 10), sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "bashar",
            text="bashar button (danger)",
            border_spacing=12,
            corner_radius=12,
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=2, column=1, padx=30, pady=(0, 10), sticky="nw")

    def _initCommands(self):
        self.ui.get("b_ledoff").setCommand(lambda: LEDService.getInstance().off())
        self.ui.get("bashar").setCommand(
            lambda: self.navigator.navigateEphemeral(
                StatImg(
                    self.appRoot,
                    ctk.CTkImage(
                        Image.open("./assets/images/bashar.png"), size=(1600, 1600)
                    ),
                )
            )
        )

    def updateGreeting(self, datetime):
        if datetime.hour >= 2 and datetime.hour < 5:
            self.greetingText.set("Still awake?! 😴")
        elif datetime.hour >= 5 and datetime.hour < 12:
            self.greetingText.set("Good Morning! 🌄")
        elif datetime.hour >= 12 and datetime.hour < 18:
            self.greetingText.set("Good Afternoon! 🌞")
        elif datetime.hour >= 18 and datetime.hour < 22:
            self.greetingText.set("Good Evening! 🌙")
        else:
            self.greetingText.set("Good Night! 💤")
