import customtkinter as ctk
from lib.CommandUI import CommandUI
from lib.DevChecks import isDev
from lib.Navigation import NavigationManager

from pages.Home import HomePage
from pages.Settings import SettingsPage

class App(ctk.CTk):
    APP_TITLE = "QuackOS"
    FONT_NAME = "Ubuntu Mono"

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("./themes/cherry.json")
        
        super().__init__()
        self.title(self.APP_TITLE)
        self.geometry("800x480")

        self.ui = CommandUI(self)

        self.nav_root = self.ui.add(ctk.CTkFrame, "nav_root", fg_color=self._fg_color)
        self.navigation: 'NavigationManager' = NavigationManager(self.nav_root)

        self._initGraphics()
        self._initCommands()
        self._addPages()

    def setFullscreen(self, fullscreen: bool):
        _setter = lambda fs: self.attributes("-fullscreen", fs)
        self.bind("<Escape>", lambda e: _setter(False))
        _setter(fullscreen)
    
    def _initGraphics(self):
        # init grid
        self.grid_columnconfigure((1), weight=1)
        self.grid_columnconfigure((0), weight=0)
        self.grid_rowconfigure((1), weight=1)
        self.grid_rowconfigure((0), weight=0)

        # grid in the nav root
        self.nav_root.grid(row=0, column=1, rowspan=4, sticky="nsew")

        # init nav sidebar
        sidebar = self.ui.add(ctk.CTkFrame, "sb_main",
                              width=140,
                              corner_radius=0
                              )
        sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        # sidebar.grid_rowconfigure(4, weight=1)

        self.ui.add(ctk.CTkLabel, "sb_title",
                    root=sidebar,
                    text=self.APP_TITLE,
                    font=(self.FONT_NAME, 24, "bold"),
                    ).grid(row=0, column=0, padx=20, pady=40, sticky="n")

        self.ui.add(ctk.CTkButton, "sb_home",
                    root=sidebar,
                    text="Home", 
                    font=(self.FONT_NAME, 18),
                    width=120, height=40,
                    corner_radius=12
                    ).grid(row=1, column=0, padx=20, pady=20, sticky="n")

        self.ui.add(ctk.CTkButton, "sb_settings", 
                    root=sidebar,
                    text="Settings",
                    font=(self.FONT_NAME, 18),
                    width=120, height=40, 
                    corner_radius=12
                    ).grid(row=3, column=0, padx=20, pady=20, sticky="s")

    def _initCommands(self):
        self.ui.addCommand("sb_home", lambda: self.navigation.navigate(HomePage))
        self.ui.addCommand("sb_settings", lambda: self.navigation.navigate(SettingsPage))

    def _addPages(self):
        self.navigation.registerPage(HomePage(self.nav_root))
        self.navigation.registerPage(SettingsPage(self.nav_root))

        self.navigation.setInitialPage(HomePage)


if __name__ == "__main__":
    app = App()
    if not isDev():
        app.setFullscreen(True)
    app.mainloop()

