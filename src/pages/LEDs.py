from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.CommandUI import CommandUI
from lib.Navigation import NavigationPage
from lib.SwappableUI import SwappableUI, SwappableUIFrame

class LEDsPage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="LEDs", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_rowconfigure(1, weight=1)

        self.ui.add(ctk.CTkLabel, "title",
                    text="💡 LEDs",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nw")
    
        self.tabview = self.ui.add(ctk.CTkTabview, "tab_main",
                    corner_radius=12,
                    ).withGridProperties(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.tabview.getInstance().add("Themes")
        self.tabview.getInstance().add("Effects")
        self.tabview.getInstance().add("Solid Colors")
        self.tabview.getInstance().add("Configure")
        self.tabview.getInstance().set("Themes")
        new_fg_color = self.tabview.getInstance()._segmented_button.cget("unselected_color")
        self.tabview.getInstance()._segmented_button.configure(
            font=(self.appRoot.FONT_NAME, 18),
            # corner_radius=12,
            height=35,
            fg_color=self.appRoot._fg_color,
            unselected_color=self.tabview.getInstance().cget("fg_color"),
            # border_width=10,
        )
        self.tabview.getInstance().configure(fg_color=new_fg_color)
        self.tabview.grid()

        self.configureTab = SwappableUI(self.tabview.getInstance().tab("Configure"))
        noauth = self.configureTab.newFrame("noauth")
        noauth.ui.add(ctk.CTkLabel, "noauth_label",
                    root=noauth,
                    text="This page is locked. Sorry!",
                    font=(self.appRoot.FONT_NAME, 18)
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        authConfigPage = self.configureTab.newFrame("auth")
        authConfigPage.ui.add(ctk.CTkLabel, "auth_label",
                              root=authConfigPage,
                              text="This is the configuration page.",
                              font=(self.appRoot.FONT_NAME, 18)
                              ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        authConfigPage.ui.add(ctk.CTkButton, "test_configure",
                              root=authConfigPage,
                              text="Test Configure",
                              font=(self.appRoot.FONT_NAME, 18),
                              width=150, height=50,
                              corner_radius=20
                              ).grid(row=1, column=0, padx=5, pady=5, sticky="sew")
        self.configureTab.swap("noauth")


    def _initCommands(self):
        self.appRoot.addLockCallback(lambda: self.configureTab.swap("noauth"))

    def onShow(self):
        self.tabview.getInstance().set("Themes")
        if self.appRoot.hasFullAccess():
            self.configureTab.swap("auth")
    
    def onHide(self):
        self.tabview.getInstance().set("Themes")
        self.configureTab.swap("noauth")
