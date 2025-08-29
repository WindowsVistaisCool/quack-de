import datetime
from typing import TYPE_CHECKING

from lib.CommandUI import CommandUI
from lib.CustomWidgets import TouchScrollableFrame

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import requests
import os
from PIL import Image
from lib.Navigation import NavigationPage


class WeatherPage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Weather", **kwargs)
        self.appRoot: "App" = appRoot

        self.entries = {}

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="Weather",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=30, pady=(20, 10), sticky="nw")

        self.tv_day = ctk.StringVar(value="Unknown Day")
        self.ui.add(
            ctk.CTkLabel,
            "day",
            textvariable=self.tv_day,
            font=(self.appRoot.FONT_NAME, 24),
        ).grid(row=0, column=1, padx=30, pady=(20, 10), sticky="ne")

        self.frameUI = CommandUI(
            self.ui.add(
                ctk.CTkScrollableFrame,
                "weather_frame",
                fg_color=self.cget("fg_color"),
            )
            .grid(row=1, column=0, columnspan=10, padx=20, pady=10, sticky="nsew")
            .getInstance()
        )
        self.frameUI.master.grid_columnconfigure(0, weight=1)
        self.frameUI.master._scrollbar.configure(width=60)

    def _initCommands(self):
        pass

    def updateTime(self, now: datetime.datetime):
        self.tv_day.set(now.strftime("%A, %B %d"))

        self.updateWeather()

        self.frameUI.clear()

        entries_copy = self.entries.copy().keys()
        for epoch in entries_copy:
            if epoch < now.timestamp():
                self.entries.pop(epoch)
            else:
                self.addEntry(epoch)

    def updateWeather(self):
        api_key = os.getenv("WEATHER_API")
        assert api_key is not None

        url = (
            f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q=auto:ip&days=2"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        forecast = data["forecast"]["forecastday"]

        for day in forecast:
            for hour in day["hour"]:
                self.entries[hour["time_epoch"]] = {
                    "datetime": datetime.datetime.fromtimestamp(hour["time_epoch"]),
                    "temp_f": hour["temp_f"],
                    "feelslike_f": hour["feelslike_f"],
                    "chance_of_rain": hour["chance_of_rain"],
                    "img": "assets/weather/" + hour["condition"]["icon"].replace("//cdn.weatherapi.com/weather/64x64/", "").replace("/", "_"),
                }

    def addEntry(self, epoch: int):
        _nextRow = self.frameUI.master.grid_size()[1] + 1

        frame = (
            self.frameUI.add(
                ctk.CTkFrame,
                f"frame_{_nextRow}",
            )
            .grid(row=_nextRow, column=0, padx=(10, 15), pady=2, sticky="we")
            .getInstance()
        )

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        self.frameUI.add(
            ctk.CTkLabel,
            f"hour_label_{_nextRow}",
            root=frame,
            text=self.entries[epoch]["datetime"].strftime("%I:%M%p %A"),
            font=(self.appRoot.FONT_NAME, 22),
        ).grid(row=0, column=0, padx=15, pady=10, sticky="we")

        self.frameUI.add(
            ctk.CTkLabel,
            f"rain_label_{_nextRow}",
            root=frame,
            text=f"{self.entries[epoch]['chance_of_rain']}%",
            font=(self.appRoot.FONT_NAME, 22),
        ).grid(row=0, column=1, padx=15, pady=10, sticky="e")

        # basically if the image fails to load, show the text
        # of what the image should be (for debug ish?)
        img = None
        try:
            img = Image.open(self.entries[epoch]["img"])
        except:
            pass
        self.frameUI.add(
            ctk.CTkLabel,
            f"weather_icon_{_nextRow}",
            root=frame,
            text=self.entries[epoch]["img"] if img is None else "",
            image=ctk.CTkImage(img, size=(64, 64)) if img is not None else None,
        ).grid(row=0, column=2, padx=(0, 0), pady=5, sticky="e")

        self.frameUI.add(
            ctk.CTkLabel,
            f"temp_label_{_nextRow}",
            root=frame,
            text=f"{int(self.entries[epoch]['temp_f'])}°F",
            font=(self.appRoot.FONT_NAME, 22),
        ).grid(row=0, column=3, padx=15, pady=10, sticky="e")
