from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import threading
import time
import tkinter as tk

from LEDService import LEDService
from lib.CustomWidgets import ToggleButton
from lib.Navigation import EphemeralPage


class VirtualLEDs(EphemeralPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Viewer", **kwargs)
        self.appRoot: "App" = appRoot

        self.enabled = False

        def thread_target():
            while self.enabled:
                self.update()
                time.sleep(0.1)

        self.getThread = lambda: threading.Thread(target=thread_target, daemon=True)

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="LED Viewer",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=30, pady=(20, 10), sticky="nsw")

        self.ui.add(
            ToggleButton,
            "toggle",
            height=40,
            text="Display LEDs",
            toggled_text="Hide LEDs",
            font=(self.appRoot.FONT_NAME, 20),
        ).grid(row=0, column=1, padx=30, pady=(20, 10), sticky="nse")

        led_frame = (
            self.ui.add(
                ctk.CTkScrollableFrame,
                "led_frame",
            )
            .grid(row=1, column=0, columnspan=2, padx=20, pady=0, sticky="nsew")
            .getInstance()
        )
        led_frame.grid_rowconfigure(0, weight=1)
        led_frame.grid_columnconfigure(0, weight=1)

        self.ledGrid = (
            self.ui.add(
                LEDGrid,
                "led_text",
                root=led_frame,
                cols=34,
                led_size=16,
                padding=1,
            )
            .grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            .getInstance()
        )
        bg = led_frame.cget("fg_color")[1]
        self.ledGrid.configure(bg=bg)

        for i in range(LEDService.LED_COUNT):
            self.ledGrid.addLED(i)
            self.ledGrid.setLED(i, bg)

    def _initCommands(self):
        def toggle_target(state):
            self.enabled = state
            if state:
                self.getThread().start()
            else:
                c = self.ledGrid.cget("bg")
                for i in range(LEDService.LED_COUNT):
                    self.ledGrid.setLED(i, c)
        self.ui.get("toggle").setCommand(toggle_target)
        self.ui.get("toggle").getInstance().toggle()

    def update(self):
        if not self.enabled:
            return

        svc = LEDService.getInstance().leds

        # colors = ["transparent"] * LEDService.LED_COUNT
        def applyColors():
            nonlocal colors
            for i, color in enumerate(colors):
                try:
                    self.ledGrid.setLED(i, color)
                except tk.TclError:
                    return
                if not self.enabled:
                    return

        # setcolors()
        colors = []
        for i in range(LEDService.LED_COUNT):
            led = svc.getPixelColor(i)
            r = (led >> 16) & 0xFF
            g = (led >> 8) & 0xFF
            b = led & 0xFF
            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            colors.append(hex_color)
        applyColors()


class LEDGrid(tk.Canvas):
    def __init__(self, master=None, cols=60, led_size=10, padding=1, **kwargs):
        super().__init__(master, **kwargs)
        self.cols = cols
        self.led_size = led_size
        self.padding = padding
        self._items = []

        self.configure(highlightthickness=0)

    def addLED(self, i):
        row = i // self.cols
        col = i % self.cols
        x0 = col * (self.led_size + self.padding)
        y0 = row * (self.led_size + self.padding)
        x1 = x0 + self.led_size
        y1 = y0 + self.led_size

        # create a rectangle; if indices gap, pad the _items list
        while len(self._items) <= i:
            self._items.append(None)

        item = self.create_rectangle(x0, y0, x1, y1, fill="#000000", outline="")
        self._items[i] = item

        # update scrollregion so parent scroll frame knows full size
        total_rows = (len(self._items) + self.cols - 1) // self.cols
        width = self.cols * (self.led_size + self.padding)
        height = total_rows * (self.led_size + self.padding)
        self.configure(
            scrollregion=(0, 0, width, height), width=min(width, 800), height=height
        )

    def setLED(self, i, color):
        if i < 0 or i >= len(self._items):
            return
        item = self._items[i]
        if item is None:
            return

        if color == self.itemcget(item, "fill"):
            return

        self.itemconfig(item, fill=color)
