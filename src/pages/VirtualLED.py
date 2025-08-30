from typing import TYPE_CHECKING

from LEDService import LEDService
from pages.ephemeral.StatImg import StatImg
from PIL import Image


if TYPE_CHECKING:
    from App import App

import customtkinter as ctk

from lib.Navigation import NavigationPage


class VirtualLEDs(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Viewer", **kwargs)
        self.appRoot: "App" = appRoot

        self.labels = []

        self.init = False

        self._initUI()
        self._initCommands()

    def _setInit(self):
        self.init = not self.init

    def _initUI(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="LED Viewer",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=30, pady=(20, 10), sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "init",
            text="do init"
        ).grid(row=0, column=1, padx=30, pady=(20, 10), sticky="ne")

        led_frame = self.ui.add(
            ctk.CTkScrollableFrame,
            "led_frame",
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew").getInstance()

        for i in range(LEDService.LED_COUNT):
            label = ctk.CTkLabel(
                master=led_frame,
                text=f" ",
                font=(self.appRoot.FONT_NAME, 14),
            )
            self.labels.append(label)
            label.grid(row=i // 60, column=i % 60, padx=1, pady=0, sticky="nw")

    def _initCommands(self):
        self.ui.get("init").setCommand(self._setInit)

    def update(self):
        if not self.init:
            return
        
        svc = LEDService.getInstance().leds
        colors = ["transparent"] * LEDService.LED_COUNT
        def setcolors():
            nonlocal colors
            for i, color in enumerate(colors):
                if self.labels[i].cget("fg_color") != color:
                    self.labels[i].configure(fg_color=color)
        # setcolors()
        colors = []
        for i in range(LEDService.LED_COUNT):
            led = svc.getPixelColor(i)
            r = (led >> 16) & 0xFF
            g = (led >> 8) & 0xFF
            b = led & 0xFF
            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            colors.append(hex_color)
        setcolors()
