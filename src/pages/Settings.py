from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import os
from Configurator import Configurator

from lib.Navigation import NavigationPage
from lib.Notifier import NotifierService
from lib.Themes import Theme

from pages.ephemeral.About import AboutPage
from pages.ephemeral.Lock import LockPage
from pages.ephemeral.YesNoDialog import YesNoDialog

class SettingsPage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Settings", **kwargs)
        self.appRoot: 'App' = appRoot

        self.hasUnsavedChanges = False
        self.old_theme = None

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)

        self.ui.add(ctk.CTkButton, "title",
                    text="⚙️ Settings",
                    fg_color=self._fg_color,
                    bg_color=self._fg_color,
                    hover_color=self._fg_color,
                    anchor="nw",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=23, pady=(27, 5), sticky="nw")
    
        self.ui.add(ctk.CTkButton, "about",
                    text=f"About {self.appRoot.APP_TITLE}",
                    font=(self.appRoot.FONT_NAME, 18),
                    width=100, height=40,
                    corner_radius=12
                    ).grid(row=0, column=1, padx=30, pady=(30, 5), sticky="ne")

        self.ui.add(ctk.CTkLabel, "l_desc",
                    text="Configure application settings here",
                    font=(self.appRoot.FONT_NAME, 16)
                    ).grid(row=1, column=0, padx=30, pady=5, sticky="nw")
    
        # copy text color from label to title
        self.ui.get("title").getInstance().configure(text_color=self.ui.get("l_desc").getInstance().cget("text_color"))

        f_settings = self.ui.add(ctk.CTkFrame, "f_settings",
                    width=400, height=50,
                    ).withGridProperties(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        f_settings.getInstance().grid_columnconfigure(0, weight=1)
        f_settings.grid()

        self.ui.add(ctk.CTkLabel, "l_theme",
                    root=f_settings.getInstance(),
                    text="Theme Settings:",
                    font=(self.appRoot.FONT_NAME, 14, "bold")
                    ).grid(row=0, column=0, padx=10, pady=5, sticky="nsw")

        self.old_theme = Theme(Configurator.getInstance().getTheme()).name
        self.om_theme = ctk.StringVar(value=self.old_theme)
        self.ui.add(ctk.CTkOptionMenu, "om_theme",
                    root=f_settings.getInstance(),
                    variable=self.om_theme,
                    values=Theme.getThemeNames(),
                    ).grid(row=1, column=0, rowspan=2, padx=10, pady=(0, 10), sticky="w")

        self.s_darkmode = ctk.BooleanVar(value=Configurator.getInstance().getAppearanceMode() == "dark")
        s_darkmode = self.ui.add(ctk.CTkSwitch, "s_darkmode",
                                 root=f_settings.getInstance(),
                                 text="Dark Mode",
                                 variable=self.s_darkmode,
                                 ).withGridProperties(row=1, column=1, padx=20, pady=(0, 10), sticky="sw")
        if self.s_darkmode.get() == "dark":
            s_darkmode.getInstance().toggle()
        s_darkmode.grid()

        self.ui.add(ctk.CTkSwitch, "s_animations",
                    root=f_settings.getInstance(),
                    text="Animations",
                    state="disabled"
                    ).grid(row=2, column=1, padx=20, pady=(0, 10), sticky="sw")

        self.lockedSettings = self.ui.add(ctk.CTkFrame, "f_deviceSettings",
                    ).withGridProperties(row=3, column=0, columnspan=2, padx=30, pady=10, sticky="we")
        self.lockedSettings.getInstance().grid_columnconfigure((0, 1), weight=1)
        self.lockedSettings.drop() # ensure frame is not loaded

        self.ui.add(ctk.CTkLabel, "l_deviceSettings",
                    root=self.lockedSettings.getInstance(),
                    text="Device Options:",
                    font=(self.appRoot.FONT_NAME, 14, "bold")
                    ).grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky="nsw")

        self.ui.add(ctk.CTkButton, "b_restartXServer",
                    root=self.lockedSettings.getInstance(),
                    text="Restart X",
                    height=40,
                    ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nse")

        self.ui.add(ctk.CTkButton, "b_restart",
                    root=self.lockedSettings.getInstance(),
                    text="Restart Device",
                    height=40,
                    fg_color=("red2", "red3"),
                    hover_color="darkred",
                    state="disabled", # disabled for "safety"
                    ).grid(row=1, column=1, padx=15, pady=(0, 10), sticky="nsw")

        self.b_save = self.ui.add(ctk.CTkButton, "save",
                    text="Save Settings",
                    height=40,
                    font=(self.appRoot.FONT_NAME, 16),
                    corner_radius=12
                    ).withGridProperties(row=4, column=0, columnspan=2, padx=30, pady=(20, 10), sticky="se")

    def _initCommands(self):
        def showLockPage():
            if self.lockedSettings.getInstance().winfo_ismapped():
                self.lockDeviceSettings()
                return

            lockPage = LockPage(self.navigator, self.appRoot, self.appRoot.content_root.getInstance())
            lockPage.addSuccessCallback(self.unlockDeviceSettings)
            lockPage.addFailureCallback(self.navigator.navigateBack)

            self.navigator.navigateEphemeral(lockPage)
        self.ui.get("title").setCommand(showLockPage)

        self.ui.get("about").setCommand(lambda: self.navigator.navigateEphemeral(
                AboutPage(self.navigator, self.appRoot, self.appRoot.content_root.getInstance())))

        def hasUnsaved():
            self.hasUnsavedChanges = True
            self.ui.get("save").grid()

        def om_callback(result: str):
            hasUnsaved()
            if result == Theme(Configurator.getInstance().getTheme()).name:
                return
            Configurator.getInstance().setTheme(Theme[result])
        self.ui.get("om_theme").setCommand(om_callback)

        def b_restartApp_callback():
            if os.name == 'nt':
                NotifierService.notify("Can't invoke that on this device!", 2000)
                return
            os.system("sudo pkill -t tty1")
        self.ui.get("b_restartXServer").setCommand(b_restartApp_callback)

        def b_restart_callback():
            def yes_callback():
                self.unlockDeviceSettings()
                if os.name == 'nt':
                    NotifierService.notify("Can't invoke that on this device!", 2000)
                    return
                os.system("sudo reboot")

            def no_callback():
                self.unlockDeviceSettings()

            dialog = YesNoDialog(self.navigator, self.appRoot, self.appRoot.content_root.getInstance())
            dialog.init(
                message="Are you sure you want to restart the device?",
                yesCallback=yes_callback,
                noCallback=no_callback
            )
            self.navigator.navigateEphemeral(dialog)
        self.ui.get("b_restart").setCommand(b_restart_callback)


        self.ui.get("s_darkmode").setCommand(hasUnsaved)

        def save_invoke():
            self.ui.get("save").drop()

            Configurator.getInstance().setAppearanceMode("dark" if self.s_darkmode.get() else "light")
            Configurator.getInstance().saveSettings()
            NotifierService.notify("Settings saved successfully!", 1500)

            ctk.set_appearance_mode(Configurator.getInstance().getAppearanceMode())
            # [TODO] this is bad because what if we are doing important things so yeah
            # if self.om_theme.get() != self.old_theme:
            #     self.ui.get("b_restartXServer").command()
        self.ui.get("save").setCommand(save_invoke)

    def unlockDeviceSettings(self):
        """Unlocks the device settings section."""
        self.lockedSettings.grid()
        self.ui.get("b_restart").getInstance().configure(state="normal")
    
    def lockDeviceSettings(self):
        """Locks the device settings section."""
        self.lockedSettings.drop()
        self.ui.get("b_restart").getInstance().configure(state="disabled")

    def onHide(self):
        self.lockDeviceSettings()
