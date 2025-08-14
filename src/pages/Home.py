from typing import TYPE_CHECKING

from LEDService import LEDService


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
        ).grid(row=0, column=0, padx=30, pady=(35, 10), sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "test",
            text="test"
        ).grid(row=1, column=0, padx=30, pady=(10, 10), sticky="nw")

    def _initCommands(self):
        self.ui.get("test").setCommand(lambda: LEDService.getInstance().test())

    def updateGreeting(self, datetime):
        if datetime.hour >= 2 and datetime.hour < 5:
            self.greetingText.set("Still awake?! 😴")
        elif datetime.hour >= 5 and datetime.hour < 12:
            self.greetingText.set("Good Morning! 🌄")
        elif datetime.hour >= 12 and datetime.hour < 18:
            self.greetingText.set("Good Afternoon! ☀️")
        elif datetime.hour >= 18 and datetime.hour < 22:
            self.greetingText.set("Good Evening! 🌙")
        else:
            self.greetingText.set("Good Night! 💤")
