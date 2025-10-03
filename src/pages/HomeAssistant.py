from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import requests
import os
from lib.Navigation import NavigationPage


class HomeAssistantPage(NavigationPage):
    IP = "192.168.1.16"

    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Home Assistant", **kwargs)

        self.appRoot: "App" = appRoot

        self.bearer_token = os.getenv("HOMEASS_BEARER")
        self.base_url = f"http://{self.IP}:8123/api/"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }

        self._initUI()
        self._initCommands()

    def _get(self, endpoint: str, data: str):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, data=data)
        return response.json()

    def _post(self, endpoint: str, data: str):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, data=data)
        return response.json()

    def _initUI(self):
        self.ui.add(ctk.CTkButton, "why_so_serious", text="Why so serious?").grid(
            row=0, column=0, padx=20, pady=20
        )

    def _initCommands(self):
        self.ui.addCommand("why_so_serious", lambda: self._get(""))
