from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import datetime
import os
import platform
import socket

if os.name == "nt":
    import ctypes

    def getBootTime():
        kernel32 = ctypes.windll.kernel32
        uptime = kernel32.GetTickCount64() / 1000
        return datetime.timedelta(seconds=uptime)

else:
    import psutil

    def getBootTime():
        boot_time = psutil.boot_time()
        return datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time)


from Configurator import Configurator

from lib.Navigation import EphemeralNavigationPage


class AboutPage(EphemeralNavigationPage):
    @staticmethod
    def getPlatformIP():
        try:
            if os.name == "nt":
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                return ip_address
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
                return ip_address
        except socket.error as e:
            return f"Error retrieving IP: {e}"

    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="About", **kwargs)
        self.appRoot: "App" = appRoot

        self.PLATFORM_TEXT = f"""OS: {platform.platform()}
Architecture: {platform.architecture()[0]}
Hostname: {platform.node()}
IP Address: {self.getPlatformIP()}
Uptime: {getBootTime()}

Configurator Schema: v{Configurator.getSchemaVersion()}
"""

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure((0), weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "title",
            text=f"💡 About {self.appRoot.APP_TITLE} {self.appRoot.VERSION}",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        self.ui.add(
            ctk.CTkLabel,
            "description",
            text=self.appRoot.APP_DESCRIPTION,
            font=(self.appRoot.FONT_NAME, 16),
        ).grid(row=1, column=0, padx=20, pady=(0, 5), sticky="nwe")

        f_specs = self.ui.add(
            ctk.CTkFrame,
            "f_specs",
            width=400,
            height=50,
        ).withGridProperties(
            row=3, column=0, columnspan=2, padx=20, pady=10, sticky="we"
        )
        f_specs.getInstance().grid_columnconfigure(0, weight=1)
        f_specs.grid()

        self.ui.add(
            ctk.CTkLabel,
            "l_specs",
            root=f_specs.getInstance(),
            text="Platform Specifications:",
            font=(self.appRoot.FONT_NAME, 16, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(5, 0), sticky="nsw")

        self.ui.add(
            ctk.CTkLabel,
            "l_specs_pc",
            root=f_specs.getInstance(),
            text=self.PLATFORM_TEXT,
            font=(self.appRoot.FONT_NAME, 14),
            justify="left",
        ).grid(row=1, column=0, padx=10, pady=(0, 5), sticky="nsw")

        self.ui.add(
            ctk.CTkButton,
            "nav_back",
            text="Back",
            font=(self.appRoot.FONT_NAME, 18),
            width=150,
            height=50,
            corner_radius=12,
        ).grid(row=4, column=0, padx=20, pady=20, sticky="s")

    def _initCommands(self):
        self.ui.addCommand(
            "nav_back",
            lambda: self.appRoot.navigation.navigate(
                type(self.appRoot.navigation.previousPage)
            ),
        )

    def onShow(self):
        self.appRoot.toggleNav(False)

    def onHide(self):
        self.appRoot.toggleNav(True)
