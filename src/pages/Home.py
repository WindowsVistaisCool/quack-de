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
            font=(self.appRoot.FONT_NAME, 40, "bold"),
            justify="center",
        ).grid(row=0, column=0, columnspan=10, padx=30, pady=(35, 25), sticky="nwe")

        self.ui.add(
            ctk.CTkLabel,
            "l_quickact",
            text="Quick Actions",
            font=(self.appRoot.FONT_NAME, 26),
        ).grid(row=1, column=0, padx=30, pady=(0, 20), sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "b_ledoff",
            text="Turn LEDs Off",
            border_spacing=12,
            corner_radius=12,
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=2, column=0, padx=30, pady=15, sticky="nw")

        self.button_fg_color = self.ui.add(
            ctk.CTkButton,
            "b_ledlow",
            text="Movie Mode",
            border_spacing=12,
            corner_radius=12,
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=3, column=0, padx=30, pady=20, sticky="nw").getInstance().cget("fg_color")

    def _initCommands(self):
        def b_ledlow_targ():
            if LEDService.getInstance().leds.getBrightness() != 20:
                LEDService.getInstance().setBrightness(20)
                self.ui.get("b_ledlow").getInstance().configure(text="Disable Movie Mode", fg_color="#FF5C5C")
            else:
                LEDService.getInstance().setBrightness(255)
                self.ui.get("b_ledlow").getInstance().configure(text="Movie Mode", fg_color=self.button_fg_color)

        self.ui.get("b_ledoff").setCommand(lambda: (LEDService.getInstance().off(), LEDService.getInstance().setBrightness(255)))
        self.ui.get("b_ledlow").setCommand(b_ledlow_targ)

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
