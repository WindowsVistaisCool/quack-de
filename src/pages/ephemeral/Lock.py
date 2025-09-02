from PIL import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import EphemeralPage


class LockPage(EphemeralPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="Lock", **kwargs)
        self.appRoot: "App" = appRoot

        self.successCallback = None
        self.failureCallback = None
        self.password = ("yes", "no", "no", "grr")
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)

        top_frame = self.ui.add(
            ctk.CTkFrame,
            "top_frame",
        ).withGridProperties(
            row=0, column=0, columnspan=10, padx=20, pady=(20, 0), sticky="new"
        )
        top_frame.grid()

        self.ui.add(
            ctk.CTkButton,
            "return",
            root=top_frame.getInstance(),
            text="Back",
            font=(self.appRoot.FONT_NAME, 18),
            height=50,
            corner_radius=12,
        ).grid(row=0, column=0, padx=15, pady=15, sticky="nsw")

        self.ui.add(
            ctk.CTkLabel,
            "description",
            root=top_frame.getInstance(),
            text="You need to enter a password to unlock this.",
            font=(self.appRoot.FONT_NAME, 20),
            justify="left",
        ).grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.grid_rowconfigure((0, 1), weight=0)
        self.grid_rowconfigure((2, 3), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.entryText = ctk.StringVar(value="")
        self.ui.add(
            ctk.CTkEntry,
            "entrybox",
            textvariable=self.entryText,
            state="disabled",
            font=(self.appRoot.FONT_NAME, 20),
            height=40,
            width=350,
        ).grid(row=1, column=0, columnspan=10, padx=20, pady=10, sticky="ns")

        self.ui.add(
            ctk.CTkButton,
            "ben_yes",
            text="",
            image=ctk.CTkImage(
                Image.open("assets/images/ben_yes.png"), size=(150, 150)
            ),
        ).grid(row=2, column=0, padx=5, pady=5, sticky="ne")

        self.ui.add(
            ctk.CTkButton,
            "ben_no",
            text="",
            image=ctk.CTkImage(
                Image.open("assets/images/ben_no.png"), size=(150, 150)
            ),
        ).grid(row=2, column=1, padx=5, pady=5, sticky="nw")

        self.ui.add(
            ctk.CTkButton,
            "ben_hohoho",
            text="",
            image=ctk.CTkImage(
                Image.open("assets/images/ben_hohoho.png"), size=(150, 150)
            ),
        ).grid(row=3, column=0, padx=5, pady=5, sticky="ne")

        self.ui.add(
            ctk.CTkButton,
            "ben_angry",
            text="",
            image=ctk.CTkImage(
                Image.open("assets/images/ben_angry.png"), size=(150, 150)
            ),
        ).grid(row=3, column=1, padx=5, pady=5, sticky="nw")

    def _initCommands(self):
        self.ui.get("return").setCommand(self.navigator.navigateBack)

        def addToPassword(value):
            self.entryText.set(
                self.entryText.get() + ("-" if self.entryText.get() else "") + value
            )
            # validation
            entry_text = self.entryText.get()
            items = entry_text.split("-")
            if len(items) > len(self.password): # reset after wrong attempt
                self.ui.get("entrybox").getInstance().configure(fg_color="black")
                self.entryText.set(items[-1])
            elif len(items) == len(self.password): # check for valid password
                if any(item != self.password[i] for i, item in enumerate(items)):
                    self.ui.get("entrybox").getInstance().configure(fg_color="red")
                    return
                self.successCallback()

        self.ui.get("ben_yes").setCommand(lambda: addToPassword("yes"))
        self.ui.get("ben_no").setCommand(lambda: addToPassword("no"))
        self.ui.get("ben_hohoho").setCommand(lambda: addToPassword("hohoho"))
        self.ui.get("ben_angry").setCommand(lambda: addToPassword("grr"))

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
            raise ValueError(
                "No success callback has been defined! This initiates a softlock."
            )
        self.appRoot.toggleNav(False)

    def onHide(self):
        self.appRoot.toggleNav(True)
