from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from lib.Navigation import NavigationPage
from lib.Notifier import NotifierService

from pages.About import AboutPage

class DebugPage(NavigationPage):
    PLATFORM_TEXT = "OS: ben\n"*10

    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Debug", **kwargs)
        self.appRoot: 'App' = appRoot
        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.ui.add(ctk.CTkLabel, "title",
                    text="hehehaw this is the debug page!!!! grrrr",
                    font=(self.appRoot.FONT_NAME, 24)
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "destroy",
                    text="destroy everything!! har har har",
                    ).grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        
        self.ui.add(ctk.CTkButton, "test_about",
                    text="Test About Page",
                    command=lambda: self.appRoot.navigation.navigate(AboutPage)
                    ).grid(row=1, column=1, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "rebuild",
                    text="magical fix everything button!!",
                    ).grid(row=2, column=0, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "cause_exception",
                    text="Cause Exception",
                    command=lambda: self.appRoot.navigation.navigate(AboutPage)
                    ).grid(row=2, column=1, padx=20, pady=20, sticky="nw")

        self.ui.add(ctk.CTkButton, "notify_test",
                    text="Notify Test"
                    ).grid(row=3, column=0, padx=20, pady=20, sticky="nw")
    
        f_specs = self.ui.add(ctk.CTkFrame, "f_specs",
                    width=400, height=50,
                    ).withGridProperties(row=4, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_specs.getInstance().grid_columnconfigure(0, weight=1)
        f_specs.grid()

        self.ui.add(ctk.CTkLabel, "l_specs",
                    root=f_specs.getInstance(),
                    text="Hardware Specifications:",
                    font=(self.appRoot.FONT_NAME, 16, "bold")
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")
    
        self.ui.add(ctk.CTkLabel, "l_specs_pc",
                    root=f_specs.getInstance(),
                    text=self.PLATFORM_TEXT,
                    font=(self.appRoot.FONT_NAME, 14),
                    justify="left"
                    ).grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsw")

    def _initCommands(self):

        def notifasodf():
            self.appRoot.navigation.navigate(AboutPage)
            NotifierService.notify("get ready for this ultra mega goofy thing")
            self.appRoot.after(3250, lambda: self.appRoot.toggleNav(True))

        self.ui.addCommand("test_about", notifasodf)

        def raise_exception():
            raise Exception("This exception is meant to happen!")
        self.ui.get("cause_exception").setCommand(raise_exception)
        
        self.ui.addCommand("notify_test", lambda: NotifierService.notify("This is a test notification! har har har!", 10000))
