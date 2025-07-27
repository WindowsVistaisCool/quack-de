from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import EphemeralNavigationPage

class LockPage(EphemeralNavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Lock", **kwargs)
        self.appRoot: 'App' = appRoot

        self.successCallback = None
        self.failureCallback = None

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)
        
        top_frame = self.ui.add(ctk.CTkFrame, "top_frame",
                                ).withGridProperties(row=0, column=0, padx=20, pady=20, sticky="new")
        top_frame.grid()

        self.ui.add(ctk.CTkButton, "return",
                    root=top_frame.getInstance(),
                    text="Back",
                    font=(self.appRoot.FONT_NAME, 18),
                    height=60,
                    corner_radius=12
                    ).grid(row=0, column=0, padx=15, pady=15, sticky="nsw")

        self.ui.add(ctk.CTkLabel, "description",
                    root=top_frame.getInstance(),
                    text="You need to enter a password to unlock this.",
                    font=(self.appRoot.FONT_NAME, 20),
                    justify="left",
                    ).grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.ui.add(ctk.CTkButton, "cheat",
                    height=100,
                    text="unlock. shh!!").grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nw")
    
    def _initCommands(self):
        self.ui.get("return").setCommand(self.navigator.navigateBack)
        self.ui.get("cheat").setCommand(self.successCallback)

    def addSuccessCallback(self, callback):
        """Sets a callback to be called on successful unlock."""
        def newCallback():
            callback()
            self.navigator.navigateBack()

        self.successCallback = newCallback
        self._initCommands()
    
    def addFailureCallback(self, callback):
        """Sets a callback to be called on failed unlock."""
        self.failureCallback = callback
        self._initCommands()

    def onShow(self):
        if not self.successCallback:
            raise ValueError("No success callback has been defined! This initiates a softlock.")
        self.appRoot.toggleNav(False)

    def onHide(self):
        self.appRoot.toggleNav(True)