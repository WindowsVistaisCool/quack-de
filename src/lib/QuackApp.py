import customtkinter as ctk

from lib.CommandUI import CommandUI
from lib.Configurator import Configurator
from lib.Navigation import NavigationManager
from lib.Notifier import NotifierService


class QuackApp(ctk.CTk):
    def __init__(self, appTitle="QuackApp", *args, **kwargs):
        self.appTitle = appTitle
        Configurator.initialize(appTitle)
        ctk.set_appearance_mode(Configurator.getInstance().getAppearanceMode())
        ctk.set_default_color_theme(Configurator.getInstance().getTheme())

        super().__init__(*args, **kwargs)

        self.title(self.appTitle)

        self.ui = CommandUI(self)

        NotifierService.setDelayFuncs(self.after, self.after_cancel)
        NotifierService.init()

        self.content_root = self.ui.add(
            ctk.CTkFrame, "nav_root", fg_color=self._fg_color
        )
        self.navigation: "NavigationManager" = NavigationManager(
            self.content_root.getInstance()
        )
        self.navigation.registerExceptionHandling()

    def setFullscreen(self, fullscreen: bool):
        _setter = lambda fs: self.attributes("-fullscreen", fs)
        self.bind("<Escape>", lambda e: _setter(False))
        _setter(fullscreen)
