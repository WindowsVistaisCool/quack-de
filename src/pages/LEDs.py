
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import time
from tkinter import PhotoImage

from LEDLoops import LEDLoops
from LEDService import LEDService

from lib.CommandUI import CommandUI
from lib.led.LEDLoop import LEDLoop
from lib.Navigation import NavigationPage
from lib.CustomWidgets import QuackColorPicker, TouchScrollableFrame, QuackExtendedButton
from lib.SwappableUI import SwappableUI

class LEDsPage(NavigationPage):
    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="LEDs", **kwargs)
        self.appRoot: 'App' = appRoot

        self.ledService = LEDService(self.appRoot)
        self.ledService.errorCallback = self.ui.exceptionCallback

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
                    ).withGridProperties(row=0, column=1, padx=(0, 10), pady=(20, 0), sticky="w")

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
        self.tabview.getInstance().add("FX")
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
        themesTab.grid_columnconfigure(0, weight=1)
        themesTab.grid_rowconfigure(0, weight=1)
        _scrollFrame = self.ui.add(TouchScrollableFrame, "scroll_filler",
                                    root=themesTab,
                                    fg_color=themesTab._fg_color,
                                    border_width=0,
                                    ).withGridProperties(row=0, column=0, padx=0, pady=0, sticky="nsew")
        _scrollFrame.getInstance().grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        _scrollFrame.getInstance().grid_columnconfigure((0, 1), weight=1)
        _scrollFrame.grid()
        themesUI = CommandUI(_scrollFrame.getInstance())

        test_themes = [
            (
                "Twinkle",
                "assets/images/christmas.png",
                (0, 0),
                LEDLoops.getLoop("twinkle"),
            ),
            (
                "Rainbow",
                "assets/images/rainbow.png",
                (0, 1),
                LEDLoops.getLoop("rainbow"),
            ),
            (
                "Rainbow Snake",
                "assets/images/snake.png",
                (1, 0),
                LEDLoops.getLoop("rgbSnake"),
            ),
            (
                "Fire 2012",
                "assets/images/fire.png",
                (1, 1),
                LEDLoops.getLoop("fire2012"),
            )
        ]

        for theme_name, image_path, location, loop in test_themes:
            _frame = themesUI.add(ctk.CTkFrame, f"f_{theme_name.lower()}",
                                   corner_radius=25
                                   ).withGridProperties(row=location[0], column=location[1], padx=(5, 10), pady=(0, 40), stick="n")
            _frame.grid()
            
            # Create long press callback for this theme
            def make_long_press_callback(loop: 'LEDLoop'):
                def exception_wrapper():
                    try:
                        self.ledService.setLoop(loop)
                        self.navigator.navigateEphemeral(loop.getSettings(self.appRoot))
                    except:
                        self.ui.exceptionCallback(traceback.format_exc())
                return exception_wrapper
            
            # Create normal command for this theme
            def make_normal_command(loop):
                def exception_wrapper():
                    try:
                        self.ledService.setLoop(loop)
                    except:
                        self.ui.exceptionCallback(traceback.format_exc())
                return exception_wrapper
            
            themesUI.add(QuackExtendedButton, f"b_{theme_name.lower()}",
                         root=_frame.getInstance(),
                         text=theme_name,
                         compound="top",
                         font=(self.appRoot.FONT_NAME, 20),
                         width=200, height=150,
                         border_spacing=0,
                         border_width=0,
                         corner_radius=0,
                         fg_color=_frame.getInstance().cget("fg_color"),
                         bg_color=_frame.getInstance().cget("fg_color"),
                         hover_color=_frame.getInstance().cget("fg_color"),
                         image=PhotoImage(file=image_path),
                         command=make_normal_command(loop),
                         longpress_callback=make_long_press_callback(loop),
                         longpress_threshold=450
                         ).grid(row=0, column=0, padx=10, pady=10)

        solidColorsTab = self.tabview.getInstance().tab("Solid Color")
        solidColorsTab.grid_columnconfigure(0, weight=1)
        self.ui.add(QuackColorPicker, "color_picker",
                                root=solidColorsTab,
                                width=380,
                                ).grid(row=0, column=0, padx=0, pady=0, sticky="")
        # TODO: set the slider to like 50% at startup

        # TODO: figure where to put this lol
        # self.ui.add(ctk.CTkButton , "b_rainbow",
        #             root=QuackColorPicker,
        #             text="Rainbow",
        #             ).grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nse")

        configUI = CommandUI(self.configFrame)
        self.configFrame.grid_rowconfigure((0, 1, 2), weight=1)
        self.configFrame.grid_rowconfigure(3, weight=1)
        self.configFrame.grid_columnconfigure(0, weight=0)
        self.configFrame.grid_columnconfigure(1, weight=1)
        _cfgTextFrame = configUI.add(ctk.CTkFrame, "cfg_text_frame",
                                    root=self.configFrame,
                                    corner_radius=12,
                                    ).withGridProperties(row=0, column=0, columnspan=2, padx=0, pady=(15, 0), sticky="new")
        _cfgTextFrame.getInstance().grid_rowconfigure(0, weight=1)
        _cfgTextFrame.getInstance().grid_columnconfigure(0, weight=1)
        _cfgTextFrame.grid()
        configUI.add(ctk.CTkLabel, "cfg_text",
                     root=_cfgTextFrame.getInstance(),
                     text="LED Information (initial values):",
                     font=(self.appRoot.FONT_NAME, 20, "bold"),
                     justify="center",
                     ).grid(row=0, column=0, padx=0, pady=(20, 0), sticky="new")
        configUI.add(ctk.CTkLabel, "cfg_text_info",
                     root=_cfgTextFrame.getInstance(),
                     text=f"""LED Count: {self.ledService.LED_COUNT}
LED Pin: {self.ledService.LED_PIN}
LED Frequency: {self.ledService.LED_FREQ_HZ} Hz
LED DMA: {self.ledService.LED_DMA}
LED Brightness: {self.ledService.LED_BRIGHTNESS}
LED Invert: {self.ledService.LED_INVERT}
LED Channel: {self.ledService.LED_CHANNEL}
""",
                     font=(self.appRoot.FONT_NAME, 14),
                     justify="left",
                     ).grid(row=1, column=0, padx=(20, 0), pady=10, sticky="nw")

        configUI.add(ctk.CTkLabel, "cfg_brightness_label",
                     root=self.configFrame,
                     text="Brightness",
                     font=(self.appRoot.FONT_NAME, 16),
                     ).grid(row=1, column=0, padx=(20, 20), pady=(0, 20), sticky="nsw")
        configUI.add(ctk.CTkSlider, "brightness_slider",
                     root=self.configFrame,
                     from_=0, to=255,
                     command=self.ledService.setBrightness,
                     number_of_steps=256,
                     width=300,
                     ).grid(row=1, column=1, padx=(20, 20), pady=(0, 20), sticky="nsew")
        configUI.get("brightness_slider").getInstance().set(self.ledService.LED_BRIGHTNESS)


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

        def solid_color_command(rgb):
            self.ledService.setSolid(*rgb)

        self.ui.get("color_picker").setCommand(solid_color_command)

    def onShow(self):
        if self.appRoot.hasFullAccess():
            self.ui.get("b_config").getInstance().configure(text="Configuration")
            self.ui.get("b_config").grid()
    
    def onHide(self):
        self.ui.get("b_config").getInstance().configure(text="Configuration")
        self.ui.get("b_config").drop()
        self.tabviewUI.setFrame("main")
