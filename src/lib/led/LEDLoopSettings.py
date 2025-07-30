from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.led.LEDLoop import LEDLoop

import customtkinter as ctk

from lib.CommandUI import CommandUI
from lib.Navigation import EphemeralNavigationPage
from lib.QuackApp import QuackApp

class LEDLoopSettings(EphemeralNavigationPage):
    def __init__(self, appRoot: 'QuackApp', loop: 'LEDLoop', *, uiFactory: callable = None, **kwargs):
        assert isinstance(appRoot, QuackApp)
        super().__init__(appRoot.navigation, appRoot.content_root.getInstance(), title="LED Loop Settings", **kwargs)
        self.appRoot = appRoot
        self.loop = loop

        self._initUI()
        
        if uiFactory:
            self.ui.get("null_desc").drop()
            uiFactory(self.ui)

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text=f"LED Settings: {self.loop.id}",
                    font=(self.appRoot.FONT_NAME, 28, "bold"),
                    justify="left"
                    ).grid(row=0, column=0, padx=30, pady=30, sticky="nw")
        self.ui.add(ctk.CTkLabel, "null_desc",
                    text="There are no settings for this LED loop.",
                    font=(self.appRoot.FONT_NAME, 16),
                    justify="left"
                    ).grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nw")
    