from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage

class HomePage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Home", **kwargs)
        self.appRoot: 'App' = appRoot

        self.greetingText = ctk.StringVar(value=f"🏠 Home")

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    textvariable=self.greetingText,
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=30, pady=(35, 10), sticky="nw")

        self.ui.add(ctk.CTkLabel, "description",
                    text=f"idk what to put here uhhh shrug ig",
                    font=(self.appRoot.FONT_NAME, 16),
                    justify="left"
                    ).place(x=30, y=85)
                    # ).grid(row=1, column=0, padx=30, pady=(0, 20), sticky="nsw")

    def _initCommands(self):
        pass

    def updateGreeting(self, datetime):
        if datetime.hour >= 5 and datetime.hour < 12:
            self.greetingText.set("Good Morning! 🌄")
        elif datetime.hour >= 12 and datetime.hour < 18:
            self.greetingText.set("Good Afternoon! ☀️")
        elif datetime.hour >= 18 and datetime.hour < 22:
            self.greetingText.set("Good Evening! 🌙")
        else:
            self.greetingText.set("Good Night! 💤")
