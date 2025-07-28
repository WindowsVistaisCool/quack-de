from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from LEDLoops import LEDLoops
import rpi_ws281x as ws
import threading
import time
import traceback
from lib.CommandUI import CommandUI
from lib.Navigation import NavigationPage
from lib.QuackColorPicker import QuackColorPicker
from lib.SwappableUI import SwappableUI

class LEDsPage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="LEDs", **kwargs)
        self.appRoot: 'App' = appRoot

        self.ledService = LEDService()
        self.ledService.loopErrCallback = self.ui.exceptionCallback

        self._initUI()
        self._initCommands()

    def _initUI(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.ui.add(ctk.CTkLabel, "title",
                    text="💡 LEDs",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsw")
        
        self.ui.add(ctk.CTkButton, "b_config",
                    text="Configuration",
                    font=(self.appRoot.FONT_NAME, 18),
                    height=40,
                    corner_radius=12,
                    ).grid(row=0, column=1, padx=(0, 10), pady=(20, 0), sticky="w")

        self.ui.add(ctk.CTkButton, "toggle_leds",
                    text="Turn Off",
                    font=(self.appRoot.FONT_NAME, 18),
                    width=120, height=50,
                    corner_radius=12
                    ).grid(row=0, column=2, padx=20, pady=(20, 0), sticky="nse")

        self.tabviewUI = SwappableUI(self)
        self.tabviewUI.grid(row=1, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")
        self.tabviewFrame = self.tabviewUI.addFrame("main")
        self.configFrame = self.tabviewUI.addFrame("config")
        self.tabviewUI.setFrame("main")

        self.tabview = self.ui.add(ctk.CTkTabview, "tab_main",
                                   root=self.tabviewFrame,
                                   corner_radius=12,
                                   ).withGridProperties(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.tabview.getInstance().add("Themes")
        # self.tabview.getInstance().add("Effects")
        self.tabview.getInstance().add("Solid Color")
        self.tabview.getInstance().set("Themes")
        new_fg_color = self.tabview.getInstance()._segmented_button.cget("unselected_color")
        self.tabview.getInstance()._segmented_button.configure(
            font=(self.appRoot.FONT_NAME, 18),
            # corner_radius=12,
            height=50,
            fg_color=self.appRoot._fg_color,
            unselected_color=self.tabview.getInstance().cget("fg_color"),
            # border_width=10,
        )
        self.tabview.getInstance().configure(fg_color=new_fg_color)
        self.tabview.grid()

        themesTab = self.tabview.getInstance().tab("Themes")
        self.themesTab = CommandUI(themesTab)
        self.themesTab.add(ctk.CTkLabel, "themes_label",
                           root=themesTab,
                           text="This is the themes page.",
                           font=(self.appRoot.FONT_NAME, 18)
                           ).grid(row=0, column=0, padx=10, pady=0, sticky="nsew")
        self.themesTab.add(ctk.CTkButton, "test_themes",
                           root=themesTab,
                           text="za rainbow",
                           font=(self.appRoot.FONT_NAME, 18),
                           width=150, height=50,
                           corner_radius=20
                           ).grid(row=1, column=0, padx=5, pady=5, sticky="sew")
        self.themesTab.add(ctk.CTkButton, "test_themes2",
                            root=themesTab,
                            text="za rainbow2",
                            font=(self.appRoot.FONT_NAME, 18),
                            width=150, height=50,
                            corner_radius=20
                            ).grid(row=2, column=0, padx=5, pady=5, sticky="sew")
    
        solidColorsTab = self.tabview.getInstance().tab("Solid Color")
        solidColorsTab.grid_columnconfigure(0, weight=1)
        self.ui.add(QuackColorPicker, "color_picker",
                                root=solidColorsTab,
                                width=380,
                                ).grid(row=0, column=0, padx=0, pady=0, sticky="")

    def _initCommands(self):
        def lockPage():
            self.tabviewUI.setFrame("main")
            self.ui.get("b_config").getInstance().configure(text="Configuration")
            self.ui.get("b_config").drop()

        self.appRoot.addLockCallback(lockPage)

        def showConfig():
            if self.tabviewUI.getCurrentFrameName() == "main":
                self.ui.get("b_config").getInstance().configure(text="Back to LEDs")
                self.tabviewUI.setFrame("config")
            else:
                self.ui.get("b_config").getInstance().configure(text="Configuration")
                self.tabviewUI.setFrame("main")

        self.ui.get("b_config").setCommand(showConfig)

        self.ui.get("toggle_leds").setCommand(self.ledService.off)

        self.themesTab.get("test_themes").setCommand(lambda: self.ledService.setLoop(LEDLoops.rainbow()))
        self.themesTab.get("test_themes2").setCommand(lambda: self.ledService.setLoop(LEDLoops.holidayTwinkle(self.appRoot.after)))

        def solid_color_command(rgb):
            self.ledService.setSolid(*rgb)

        self.ui.get("color_picker").setCommand(solid_color_command)

    def onShow(self):
        if self.appRoot.hasFullAccess():
            self.ui.get("b_config").grid()
    
    def onHide(self):
        self.ui.get("b_config").drop()
        self.tabviewUI.setFrame("main")

class LEDService:
    LED_COUNT = 50
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 200 # 0-255
    LED_INVERT = False
    LED_CHANNEL = 0

    def __init__(self):
        self.leds = ws.PixelStrip(
            self.LED_COUNT, 
            self.LED_PIN, 
            self.LED_FREQ_HZ, 
            self.LED_DMA, 
            self.LED_INVERT, 
            self.LED_BRIGHTNESS, 
            self.LED_CHANNEL
        )
        self.leds.begin()
        
        self.loop = LEDLoops.null()
        self._breakLoopEvent = threading.Event()
        self._isInLoop = False
        self._isChangingLoop = False
        self.loopThread = None

        self.loopErrCallback = lambda e: print(e)

        self._createLoopThread()
        self.loopThread.start()
    
    def _createLoopThread(self):
        self.loopThread = threading.Thread(target=self._ledLoopTarget, daemon=True)

    def _ledLoopTarget(self):
        self._isInLoop = True
        while not self._breakLoopEvent.is_set():
            time.sleep(0.05)  # Sleep to prevent busy waiting
            try:
                finished = self.loop(self.leds, self._breakLoopEvent)
                if finished is True:
                    self._breakLoopEvent.set()
            except Exception:
                self.loopErrCallback(traceback.format_exc())
                break
        self._isInLoop = False
        
    def setLoop(self, callable):
        self._breakLoopEvent.set()

        # ensure this is not called multiple times
        if self._isChangingLoop:
            return

        self._isChangingLoop = True

        timeout = time.time() + 2
        while self._isInLoop and time.time() < timeout:
            time.sleep(0.1)

        if self._isInLoop:
            raise RuntimeError("LED loop is still running after 2 seconds. This should not happen.")

        self._breakLoopEvent.clear()

        if not callable:
            callable = LEDLoops.null()
        self.loop = callable

        self._createLoopThread()
        self.loopThread.start()

        self._isChangingLoop = False

    def setSolid(self, r: int, g: int, b: int):
        if self.loopThread:
            if self.loopThread.is_alive():
                self.setLoop(LEDLoops.null())
        for i in range(self.LED_COUNT):
            self.leds.setPixelColor(i, ws.Color(r, g, b))
        self.leds.show()
    
    def off(self):
        self.setSolid(0, 0, 0)
