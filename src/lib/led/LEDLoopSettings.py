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
        self._initCommands()
        
        if uiFactory:
            self.ui.get("null_desc").drop()

            uiFactory(CommandUI(self.ui.get("f_main").getInstance()))

    def _initUI(self):

        top_frame = self.ui.add(ctk.CTkFrame, "top_frame",
                                ).grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.ui.add(ctk.CTkButton, "return",
                    root=top_frame.getInstance(),
                    text="Back",
                    font=(self.appRoot.FONT_NAME, 18),
                    height=60,
                    corner_radius=12
                    ).grid(row=0, column=0, padx=15, pady=15, sticky="nsw")

        self.ui.add(ctk.CTkLabel, "description",
                    root=top_frame.getInstance(),
                    text=f"\"{self.loop.id}\" Settings",
                    font=(self.appRoot.FONT_NAME, 28, "bold"),
                    justify="left",
                    ).grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.ui.add(ctk.CTkLabel, "null_desc",
                    text="There are no settings for this LED loop.",
                    font=(self.appRoot.FONT_NAME, 16),
                    justify="left"
                    ).grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nw")
    
        _frame = self.ui.add(ctk.CTkFrame, "f_main").grid(row=1, column=0, padx=20, pady=20, sticky="new")
        _frame.getInstance().columnconfigure(0, weight=0)
        _frame.getInstance().columnconfigure(1, weight=1)
    
    def _initCommands(self):
        self.ui.get("return").setCommand(self.navigator.navigateBack)