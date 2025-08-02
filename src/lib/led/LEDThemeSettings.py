from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.led.LEDTheme import LEDTheme

import customtkinter as ctk

from lib.CommandUI import CommandUI
from lib.Navigation import EphemeralNavigationPage
from lib.Notifier import NotifierService
from lib.QuackApp import QuackApp


class LEDThemeSettings(EphemeralNavigationPage):
    def __init__(
        self,
        appRoot: "QuackApp",
        theme: "LEDTheme",
        *,
        uiFactory: callable = None,
        **kwargs,
    ):
        assert isinstance(appRoot, QuackApp)
        super().__init__(
            appRoot.navigation,
            appRoot.content_root.getInstance(),
            title="LED Loop Settings",
            **kwargs,
        )
        self.appRoot = appRoot
        self.theme = theme

        self._initUI()
        self._initCommands()

        if uiFactory:
            self.ui.get("null_desc").drop()
            self.ui.get("f_main").grid()

            def cmdWrapper(command):
                def tgt(*args, **kwargs):
                    self.ui.get("save").grid()
                    command(*args, **kwargs)

                return tgt

            uiFactory(
                theme=self.theme,
                ui=CommandUI(self.ui.get("f_main").getInstance()),
                withShowSaveButton=cmdWrapper,
            )

    def _initUI(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        top_frame = self.ui.add(
            ctk.CTkFrame,
            "top_frame",
        ).grid(row=0, column=0, padx=20, pady=20, sticky="new")
        top_frame.getInstance().grid_columnconfigure(0, weight=0)
        top_frame.getInstance().grid_columnconfigure(1, weight=1)
        top_frame.getInstance().grid_columnconfigure(2, weight=0)

        self.ui.add(
            ctk.CTkButton,
            "return",
            root=top_frame.getInstance(),
            text="Back",
            font=(self.appRoot.FONT_NAME, 18),
            height=40,
            corner_radius=12,
        ).grid(row=0, column=0, padx=(15, 0), pady=15, sticky="nsw")

        self.ui.add(
            ctk.CTkLabel,
            "description",
            root=top_frame.getInstance(),
            text=f"{self.theme.friendlyName}",
            font=(self.appRoot.FONT_NAME, 20, "bold"),
            justify="center",
        ).grid(row=0, column=1, padx=20, pady=15, sticky="nsew")

        self.ui.add(
            ctk.CTkButton,
            "save",
            root=top_frame.getInstance(),
            text="Save",
            font=(self.appRoot.FONT_NAME, 18),
            height=40,
            corner_radius=12,
        ).withGridProperties(row=0, column=2, padx=(0, 15), pady=15, sticky="nse")

        self.ui.add(
            ctk.CTkLabel,
            "null_desc",
            text=f'There are no settings for "{self.theme.friendlyName }".',
            font=(self.appRoot.FONT_NAME, 18),
            justify="center",
        ).grid(row=1, column=0, padx=30, pady=(0, 30), sticky="new")

        _frame = self.ui.add(ctk.CTkFrame, "f_main").withGridProperties(
            row=1, column=0, padx=20, pady=(0, 20), sticky="new"
        )
        _frame.getInstance().columnconfigure(0, weight=0)
        _frame.getInstance().columnconfigure(1, weight=1)

    def _initCommands(self):
        def save_callback():
            self.ui.get("save").drop()
            NotifierService.notify(
                f"{self.theme.friendlyName} settings saved successfully.", 1500
            )
            self.theme.saveData()
            self.appRoot.navigation.navigateBack()

        self.ui.get("return").setCommand(self.navigator.navigateBack)
        self.ui.get("save").setCommand(save_callback)
