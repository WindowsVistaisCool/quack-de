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
                TouchScrollableFrame,
                "weather_frame",
                fg_color=self.cget("fg_color"),
            )
            .grid(row=1, column=0, columnspan=10, padx=20, pady=10, sticky="nsew")
            .getInstance()
        )
        self.frameUI.master.grid_columnconfigure(0, weight=1)

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

        # self.entries = {1756267200: {'datetime': datetime.datetime(2025, 8, 27, 0, 0), 'temp_f': 56.7, 'feelslike_f': 55.9, 'img': 'assets/weather/night_116.png'}, 1756270800: {'datetime': datetime.datetime(2025, 8, 27, 1, 0), 'temp_f': 54.3, 'feelslike_f': 53.2, 'img': 'assets/weather/night_113.png'}, 1756274400: {'datetime': datetime.datetime(2025, 8, 27, 2, 0), 'temp_f': 52.4, 'feelslike_f': 51.1, 'img': 'assets/weather/night_113.png'}, 1756278000: {'datetime': datetime.datetime(2025, 8, 27, 3, 0), 'temp_f': 50.9, 'feelslike_f': 49.3, 'img': 'assets/weather/night_113.png'}, 1756281600: {'datetime': datetime.datetime(2025, 8, 27, 4, 0), 'temp_f': 48.4, 'feelslike_f': 46.2, 'img': 'assets/weather/night_113.png'}, 1756285200: {'datetime': datetime.datetime(2025, 8, 27, 5, 0), 'temp_f': 46.7, 'feelslike_f': 44.3, 'img': 'assets/weather/night_113.png'}, 1756288800: {'datetime': datetime.datetime(2025, 8, 27, 6, 0), 'temp_f': 45.4, 'feelslike_f': 42.8, 'img': 'assets/weather/night_113.png'}, 1756292400: {'datetime': datetime.datetime(2025, 8, 27, 7, 0), 'temp_f': 45.7, 'feelslike_f': 43.6, 'img': 'assets/weather/day_113.png'}, 1756296000: {'datetime': datetime.datetime(2025, 8, 27, 8, 0), 'temp_f': 49.4, 'feelslike_f': 47.9, 'img': 'assets/weather/day_113.png'}, 1756299600: {'datetime': datetime.datetime(2025, 8, 27, 9, 0), 'temp_f': 54.8, 'feelslike_f': 54.1, 'img': 'assets/weather/day_113.png'}, 1756303200: {'datetime': datetime.datetime(2025, 8, 27, 10, 0), 'temp_f': 61.2, 'feelslike_f': 60.9, 'img': 'assets/weather/day_113.png'}, 1756306800: {'datetime': datetime.datetime(2025, 8, 27, 11, 0), 'temp_f': 66.8, 'feelslike_f': 66.6, 'img': 'assets/weather/day_113.png'}, 1756310400: {'datetime': datetime.datetime(2025, 8, 27, 12, 0), 'temp_f': 70.9, 'feelslike_f': 70.8, 'img': 'assets/weather/day_113.png'}, 1756314000: {'datetime': datetime.datetime(2025, 8, 27, 13, 0), 'temp_f': 72.1, 'feelslike_f': 74.2, 'img': 'assets/weather/day_113.png'}, 1756317600: {'datetime': datetime.datetime(2025, 8, 27, 14, 0), 'temp_f': 73.0, 'feelslike_f': 75.1, 'img': 'assets/weather/day_119.png'}, 1756321200: {'datetime': datetime.datetime(2025, 8, 27, 15, 0), 'temp_f': 73.5, 'feelslike_f': 75.5, 'img': 'assets/weather/day_119.png'}, 1756324800: {'datetime': datetime.datetime(2025, 8, 27, 16, 0), 'temp_f': 73.7, 'feelslike_f': 75.8, 'img': 'assets/weather/day_119.png'}, 1756328400: {'datetime': datetime.datetime(2025, 8, 27, 17, 0), 'temp_f': 73.5, 'feelslike_f': 75.8, 'img': 'assets/weather/day_122.png'}, 1756332000: {'datetime': datetime.datetime(2025, 8, 27, 18, 0), 'temp_f': 72.5, 'feelslike_f': 75.7, 'img': 'assets/weather/day_122.png'}, 1756335600: {'datetime': datetime.datetime(2025, 8, 27, 19, 0), 'temp_f': 69.9, 'feelslike_f': 69.9, 'img': 'assets/weather/day_119.png'}, 1756339200: {'datetime': datetime.datetime(2025, 8, 27, 20, 0), 'temp_f': 67.1, 'feelslike_f': 67.1, 'img': 'assets/weather/day_116.png'}, 1756342800: {'datetime': datetime.datetime(2025, 8, 27, 21, 0), 'temp_f': 64.0, 'feelslike_f': 64.7, 'img': 'assets/weather/night_113.png'}, 1756346400: {'datetime': datetime.datetime(2025, 8, 27, 22, 0), 'temp_f': 62.5, 'feelslike_f': 62.5, 'img': 'assets/weather/night_113.png'}, 1756350000: {'datetime': datetime.datetime(2025, 8, 27, 23, 0), 'temp_f': 60.3, 'feelslike_f': 59.6, 'img': 'assets/weather/night_113.png'}, 1756353600: {'datetime': datetime.datetime(2025, 8, 28, 0, 0), 'temp_f': 58.6, 'feelslike_f': 57.3, 'img': 'assets/weather/night_113.png'}, 1756357200: {'datetime': datetime.datetime(2025, 8, 28, 1, 0), 'temp_f': 57.5, 'feelslike_f': 55.9, 'img': 'assets/weather/night_113.png'}, 1756360800: {'datetime': datetime.datetime(2025, 8, 28, 2, 0), 'temp_f': 57.8, 'feelslike_f': 56.0, 'img': 'assets/weather/night_116.png'}, 1756364400: {'datetime': datetime.datetime(2025, 8, 28, 3, 0), 'temp_f': 57.2, 'feelslike_f': 55.3, 'img': 'assets/weather/night_116.png'}, 1756368000: {'datetime': datetime.datetime(2025, 8, 28, 4, 0), 'temp_f': 56.8, 'feelslike_f': 54.7, 'img': 'assets/weather/night_116.png'}, 1756371600: {'datetime': datetime.datetime(2025, 8, 28, 5, 0), 'temp_f': 56.4, 'feelslike_f': 54.3, 'img': 'assets/weather/night_116.png'}, 1756375200: {'datetime': datetime.datetime(2025, 8, 28, 6, 0), 'temp_f': 56.3, 'feelslike_f': 54.2, 'img': 'assets/weather/night_116.png'}, 1756378800: {'datetime': datetime.datetime(2025, 8, 28, 7, 0), 'temp_f': 57.0, 'feelslike_f': 55.1, 'img': 'assets/weather/day_119.png'}, 1756382400: {'datetime': datetime.datetime(2025, 8, 28, 8, 0), 'temp_f': 58.6, 'feelslike_f': 57.7, 'img': 'assets/weather/day_119.png'}, 1756386000: {'datetime': datetime.datetime(2025, 8, 28, 9, 0), 'temp_f': 58.7, 'feelslike_f': 57.3, 'img': 'assets/weather/day_122.png'}, 1756389600: {'datetime': datetime.datetime(2025, 8, 28, 10, 0), 'temp_f': 60.6, 'feelslike_f': 59.8, 'img': 'assets/weather/day_122.png'}, 1756393200: {'datetime': datetime.datetime(2025, 8, 28, 11, 0), 'temp_f': 63.3, 'feelslike_f': 62.9, 'img': 'assets/weather/day_296.png'}, 1756396800: {'datetime': datetime.datetime(2025, 8, 28, 12, 0), 'temp_f': 65.4, 'feelslike_f': 65.2, 'img': 'assets/weather/day_122.png'}, 1756400400: {'datetime': datetime.datetime(2025, 8, 28, 13, 0), 'temp_f': 66.8, 'feelslike_f': 66.7, 'img': 'assets/weather/day_122.png'}, 1756404000: {'datetime': datetime.datetime(2025, 8, 28, 14, 0), 'temp_f': 67.8, 'feelslike_f': 67.8, 'img': 'assets/weather/day_353.png'}, 1756407600: {'datetime': datetime.datetime(2025, 8, 28, 15, 0), 'temp_f': 68.8, 'feelslike_f': 68.8, 'img': 'assets/weather/day_122.png'}, 1756411200: {'datetime': datetime.datetime(2025, 8, 28, 16, 0), 'temp_f': 70.1, 'feelslike_f': 70.1, 'img': 'assets/weather/day_119.png'}, 1756414800: {'datetime': datetime.datetime(2025, 8, 28, 17, 0), 'temp_f': 69.6, 'feelslike_f': 69.6, 'img': 'assets/weather/day_116.png'}, 1756418400: {'datetime': datetime.datetime(2025, 8, 28, 18, 0), 'temp_f': 67.1, 'feelslike_f': 67.1, 'img': 'assets/weather/day_119.png'}, 1756422000: {'datetime': datetime.datetime(2025, 8, 28, 19, 0), 'temp_f': 65.2, 'feelslike_f': 65.2, 'img': 'assets/weather/day_119.png'}, 1756425600: {'datetime': datetime.datetime(2025, 8, 28, 20, 0), 'temp_f': 62.6, 'feelslike_f': 62.0, 'img': 'assets/weather/day_116.png'}, 1756429200: {'datetime': datetime.datetime(2025, 8, 28, 21, 0), 'temp_f': 60.6, 'feelslike_f': 59.2, 'img': 'assets/weather/night_116.png'}, 1756432800: {'datetime': datetime.datetime(2025, 8, 28, 22, 0), 'temp_f': 55.4, 'feelslike_f': 53.4, 'img': 'assets/weather/night_116.png'}, 1756436400: {'datetime': datetime.datetime(2025, 8, 28, 23, 0), 'temp_f': 55.2, 'feelslike_f': 52.9, 'img': 'assets/weather/night_113.png'}}
        # return

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
