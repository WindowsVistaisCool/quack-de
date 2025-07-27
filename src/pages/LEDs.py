from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import rpi_ws281x as ws
import threading
import time
import traceback
from lib.CommandUI import CommandUI
from lib.Navigation import NavigationPage
from lib.SwappableUI import SwappableUI, SwappableUIFrame

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

        self.ui.add(ctk.CTkLabel, "title",
                    text="💡 LEDs",
                    font=(self.appRoot.FONT_NAME, 32, "bold")
                    ).grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsw")
        
        self.ui.add(ctk.CTkButton, "toggle_leds",
                    text="Turn Off",
                    font=(self.appRoot.FONT_NAME, 18),
                    width=90, height=35,
                    corner_radius=12
                    ).grid(row=0, column=1, padx=20, pady=(20, 0), sticky="nse")
    
        self.tabview = self.ui.add(ctk.CTkTabview, "tab_main",
                    corner_radius=12,
                    ).withGridProperties(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")
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

        themesTab = self.tabview.getInstance().tab("Themes")
        self.themesTab = CommandUI(themesTab)
        self.themesTab.add(ctk.CTkLabel, "themes_label",
                           root=themesTab,
                           text="This is the themes page.",
                           font=(self.appRoot.FONT_NAME, 18)
                           ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.themesTab.add(ctk.CTkButton, "test_themes",
                           root=themesTab,
                           text="Test ocean theme!!!!!!",
                           font=(self.appRoot.FONT_NAME, 18),
                           width=150, height=50,
                           corner_radius=20
                           ).grid(row=1, column=0, padx=5, pady=5, sticky="sew")
    
        solidColorsTab = self.tabview.getInstance().tab("Solid Colors")
        solidColorsTab.grid_columnconfigure(0, weight=1)
        self.solidColorsTab = CommandUI(solidColorsTab)
        self.solidColorsTab.add(ctk.CTkSlider, "slider_r",
                                root=solidColorsTab,
                                from_=0, to=255,
                                ).grid(row=0, column=0, padx=20, pady=10, sticky="new")
        self.solidColorsTab.add(ctk.CTkSlider, "slider_g",
                                root=solidColorsTab,
                                from_=0, to=255,
                                ).grid(row=1, column=0, padx=20, pady=10, sticky="new")
        self.solidColorsTab.add(ctk.CTkSlider, "slider_b",
                                root=solidColorsTab,
                                from_=0, to=255,
                                ).grid(row=2, column=0, padx=20, pady=10, sticky="new")

        self.configureTab = SwappableUI(self.tabview.getInstance().tab("Configure"))
        noauth = self.configureTab.newFrame("noauth")
        noauth.ui.add(ctk.CTkLabel, "noauth_label",
                    root=noauth,
                    text="This page is locked. Sorry!",
                    font=(self.appRoot.FONT_NAME, 18)
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.authConfigPage = self.configureTab.newFrame("auth")
        self.authConfigPage.grid_rowconfigure(0, weight=0)
        self.authConfigPage.grid_rowconfigure(10, weight=1)
        self.authConfigPage.ui.add(ctk.CTkLabel, "l_actions",
                              root=self.authConfigPage,
                              text="Socket Actions",
                              font=(self.appRoot.FONT_NAME, 18),
                              ).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nw")
        self.configureTab.swap("noauth")


    def _initCommands(self):
        self.appRoot.addLockCallback(lambda: self.configureTab.swap("noauth"))

        self.ui.get("toggle_leds").setCommand(self.ledService.off)

        self.themesTab.get("test_themes").setCommand(lambda: self.ledService.setLoop(LEDLoops.rainbow()))

        def solid_color_command(_):
            r = self.solidColorsTab.get("slider_r").getInstance().get()
            g = self.solidColorsTab.get("slider_g").getInstance().get()
            b = self.solidColorsTab.get("slider_b").getInstance().get()
            self.ledService.setSolid(int(r), int(g), int(b))

        self.solidColorsTab.get("slider_r").setCommand(solid_color_command)
        self.solidColorsTab.get("slider_g").setCommand(solid_color_command)
        self.solidColorsTab.get("slider_b").setCommand(solid_color_command)

    def onShow(self):
        # self.tabview.getInstance().set("Themes")
        if self.appRoot.hasFullAccess():
            self.configureTab.swap("auth")
    
    def onHide(self):
        # self.tabview.getInstance().set("Themes")
        self.configureTab.swap("noauth")
        
class LEDService:
    LED_COUNT = 30
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 128
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
                self.leds.fill(ws.Color(0, 0, 0))  # Turn off LEDs when breaking the loop
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

class LEDLoops:
    @staticmethod
    def _wheel(pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return ws.Color(pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return ws.Color(255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return ws.Color(0, pos * 3, 255 - pos * 3)

    @staticmethod
    def null():
        return lambda *_ : True

    @classmethod
    def rainbow(cls, iterations=1):
        iterations = int(iterations)
        def target(leds: 'ws.PixelStrip', break_event: 'threading.Event'):
            for j in range(256 * iterations):
                if break_event.is_set():
                    return True
                for i in range(leds.numPixels()):
                    leds.setPixelColor(i, cls._wheel(((i * 256 // iterations) + j) & 255))
                leds.show()
                time.sleep(20 / 1000.0)  # 20 ms delay
        return target

    @classmethod
    def rainbow2(cls, wait_ms=50):
        wait_ms = int(wait_ms)
        def target(leds: 'ws.PixelStrip', break_event: 'threading.Event'):
            """Rainbow movie theater light style chaser animation."""
            for j in range(256):
                if break_event.is_set():
                    return True
                for q in range(3):
                    if break_event.is_set():
                        return True
                    for i in range(0, leds.numPixels(), 3):
                        leds.setPixelColor(i + q, cls._wheel((i + j) % 255))
                    leds.show()
                    time.sleep(wait_ms / 1000.0)
                    for i in range(0, leds.numPixels(), 3):
                        leds.setPixelColor(i + q, 0)
        return target
    