from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import EphemeralNavigationPage

class StatImg(EphemeralNavigationPage):
    def __init__(self, appRoot: "App", img, **kwargs):
        super().__init__(appRoot.navigation, appRoot.content_root.getInstance(), title="StatImg", **kwargs)

        self.appRoot = appRoot

        self.image = img

        self._initUI()

    def _initUI(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # add image
        self.ui.add(
            ctk.CTkLabel,
            "stat_img",
            image=self.image,
            text="",
        ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
