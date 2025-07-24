import customtkinter as ctk
from lib.Navigation import NavigationPage

class SettingsPage(NavigationPage):
    def __init__(self, master, **kwargs):
        super().__init__(master, title="Settings", **kwargs)
        self._initUI()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text="Settings Page"
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")
