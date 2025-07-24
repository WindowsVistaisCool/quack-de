import customtkinter as ctk
from lib.CommandUI import CommandUI
from lib.DevChecks import isDev
from lib.Navigation import NavigationManager

from pages.Home import HomePage
from pages.Settings import SettingsPage
from pages.Debug import DebugPage

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

        self.content_root = self.ui.add(ctk.CTkFrame, "nav_root", fg_color=self._fg_color)
        self.navigation: 'NavigationManager' = NavigationManager(self.content_root.getInstance())

        self._initUI()
        self._initCommands()
        self._addPages()

    def setFullscreen(self, fullscreen: bool):
        _setter = lambda fs: self.attributes("-fullscreen", fs)
        self.bind("<Escape>", lambda e: _setter(False))
        _setter(fullscreen)
    
    def _initUI(self):
        # init grid
        self.grid_columnconfigure((0), weight=0)
        self.grid_columnconfigure((1), weight=1)
        self.grid_rowconfigure((0), weight=1)

        # grid in the nav root
        self.content_root.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.content_root.getInstance().grid_rowconfigure((0), weight=1)
        self.content_root.getInstance().grid_columnconfigure((0), weight=1)

        # init nav sidebar
        self.navbar = self.ui.add(ctk.CTkFrame, "sb_main",
                              width=800,
                              corner_radius=0)
        self.navbar.grid(row=0, column=0, sticky="nsew")
        self.navbar.getInstance().grid_rowconfigure((2), weight=1)

        self.ui.add(ctk.CTkLabel, "nav_title",
                    root=self.navbar.getInstance(),
                    text=self.APP_TITLE,
                    font=(self.FONT_NAME, 24, "bold"),
                    ).grid(row=0, column=0, padx=20, pady=40, sticky="new")

        self.ui.add(ctk.CTkButton, "nav_home",
                    root=self.navbar.getInstance(),
                    text="Home", 
                    font=(self.FONT_NAME, 18),
                    width=150, height=50,
                    corner_radius=12
                    ).grid(row=1, column=0, padx=30, pady=20, sticky="new")

        self.ui.add(ctk.CTkButton, "nav_settings", 
                    root=self.navbar.getInstance(),
                    text="Settings",
                    font=(self.FONT_NAME, 18),
                    width=150, height=50, 
                    corner_radius=12
                    ).grid(row=2, column=0, padx=30, pady=40, sticky="s")

    def _initCommands(self):

        self.ui.addCommand("nav_home", lambda: self.navigation.navigate(HomePage))
        self.ui.addCommand("nav_settings", lambda: self.navigation.navigate(SettingsPage))

    def _addPages(self):
        self.navigation.registerPage(HomePage(self, self.content_root.getInstance()))
        self.navigation.registerPage(SettingsPage(self, self.content_root.getInstance()))
        self.navigation.registerPage(DebugPage(self, self.content_root.getInstance()))

        self.navigation.navigate(HomePage)


if __name__ == "__main__":
    app = App()
    # if not isDev():
    #     app.setFullscreen(True)
    app.mainloop()

