from time import time
from typing import TYPE_CHECKING

from lib.CustomWidgets import ToggleButton
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
        self.grid_rowconfigure(10, weight=1)

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

        self.button_fg_color = (
            self.ui.add(
                ToggleButton,
                "b_ledlow",
                text="Movie Mode",
                toggled_text="Bright Mode",
                border_spacing=12,
                corner_radius=12,
                font=(self.appRoot.FONT_NAME, 24),
            )
            .grid(row=3, column=0, padx=30, pady=20, sticky="nw")
            .getInstance()
            .cget("fg_color")
        )

        self.svc_status = self.ui.add(
            ctk.CTkFrame,
            "svc_status",
            corner_radius=0,
        ).grid(row=10, column=0, padx=0, pady=0, sticky="swe").getInstance()

        self.ui.add(
            ctk.CTkLabel,
            "label_svc_status",
            root=self.svc_status,
            text="Service Status:",
            font=(self.appRoot.FONT_NAME, 12),
        ).grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        tv_status = ctk.StringVar(value="unkonwn")
        self.ui.add(
            ctk.CTkLabel,
            "label_svc_status_value",
            root=self.svc_status,
            textvariable=tv_status,
            font=(self.appRoot.FONT_NAME, 12),
        ).grid(row=0, column=1, padx=5, pady=5, sticky="nw")
        self.appRoot.leds.onConnect = lambda: tv_status.set("Connected")
        self.appRoot.leds.onDisconnect = lambda: tv_status.set("Disconnected")
        self.appRoot.leds.exceptionCall = lambda e: tv_status.set(f"{e}")
        self.appRoot.leds.begin()

    def _initCommands(self):
        def b_ledlow_targ(state):
            if state:
                self.appRoot.leds.setBrightness(10)
            else:
                self.appRoot.leds.setBrightness(255)

        self.ui.get("b_ledoff").setCommand(
            lambda: (
                self.appRoot.leds.off(),
                self.ui.get("b_ledlow").getInstance().toggle(False),
            )
        )
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
