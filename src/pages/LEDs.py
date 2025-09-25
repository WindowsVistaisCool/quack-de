import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
from PIL import Image

from LEDThemes import LEDThemes

from lib.CommandUI import CommandUI
from lib.led.LEDTheme import LEDTheme
from lib.Navigation import NavigationPage
from lib.CustomWidgets import (
    QuackColorPicker,
    TouchScrollableFrame,
    QuackExtendedButton,
)
from lib.SwappableUI import SwappableUI


class LEDsPage(NavigationPage):
    def __init__(self, navigator, appRoot: "App", master, **kwargs):
        super().__init__(navigator, master, title="LEDs", **kwargs)
        self.appRoot: "App" = appRoot

        self._loadedThemeCount = 0

        self._initUI()
        self._initCommands()

        # defines how the themes are arranged in the UI
        # goes (0, 0), (0, 1), (1, 0), (1, 1), etc. in grid units
        arrangement = (
            LEDThemes.getTheme("twinkle"),
            LEDThemes.getTheme("pacifica"),
            LEDThemes.getTheme("rgbSnake"),
            LEDThemes.getTheme("fire2012"),
            LEDThemes.getTheme("rainbow"),
            # LEDThemes.getTheme("epilepsy"),
            # LEDThemes.getTheme("ledSelector"),
        )
        for theme in arrangement:
            self.addTheme(theme)

    def _initUI(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.ui.add(
            ctk.CTkLabel,
            "title",
            text="💡 LEDs",
            font=(self.appRoot.FONT_NAME, 32, "bold"),
        ).grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsw")

        self.ui.add(
            ctk.CTkButton,
            "b_config",
            text="Configuration",
            font=(self.appRoot.FONT_NAME, 18),
            height=40,
            corner_radius=12,
        ).withGridProperties(row=0, column=3, padx=20, pady=(20, 0), sticky="nse")

        self.ui.add(
            ctk.CTkLabel,
            "l_currentSeg",
            text="Sublength: ",
            font=(self.appRoot.FONT_NAME, 18, "bold"),
        ).grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.tv_segmentNum = ctk.IntVar(value=-1)
        self.tv_segmentLabel = ctk.StringVar(value="All")
        self.ui.add(
            ctk.CTkLabel,
            "currentSegment",
            textvariable=self.tv_segmentLabel,
            font=(self.appRoot.FONT_NAME, 18),
        ).grid(row=0, column=2, padx=(0, 20), pady=(20, 0), sticky="nsew")

        self.tabviewUI = SwappableUI(self)
        self.tabviewUI.grid(
            row=1, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="nsew"
        )
        self.tabviewFrame = self.tabviewUI.addFrame("main")
        self.configFrame = self.tabviewUI.addFrame("config")
        self.tabviewUI.setFrame("main")

        self.tabview = self.ui.add(
            ctk.CTkTabview,
            "tab_main",
            root=self.tabviewFrame,
            corner_radius=12,
        ).withGridProperties(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.tabview.getInstance().add("Themes")
        self.tabview.getInstance().add("Solid Color")
        # self.tabview.getInstance().add("Segments")
        self.tabview.getInstance().set("Themes")
        new_fg_color = self.tabview.getInstance()._segmented_button.cget(
            "unselected_color"
        )
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
        _scrollFrame = self.ui.add(
            TouchScrollableFrame,
            "scroll_filler",
            root=themesTab,
            fg_color=themesTab._fg_color,
            border_width=0,
        ).grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        _scrollFrame.getInstance().grid_columnconfigure((0, 1), weight=1)
        self.themesUI = CommandUI(_scrollFrame.getInstance())

        solidColorsTab = self.tabview.getInstance().tab("Solid Color")
        solidColorsTab.grid_columnconfigure(0, weight=1)
        self.ui.add(
            QuackColorPicker,
            "color_picker",
            root=solidColorsTab,
            width=380,
        ).grid(row=0, column=0, padx=0, pady=0, sticky="")

        """Config Ui page"""
        configUI = CommandUI(self.configFrame)
        self.configFrame.grid_rowconfigure((0, 1, 2), weight=1)
        self.configFrame.grid_rowconfigure(3, weight=1)
        self.configFrame.grid_columnconfigure(0, weight=0)
        self.configFrame.grid_columnconfigure(1, weight=1)
        _cfgTextFrame = configUI.add(
            ctk.CTkFrame,
            "cfg_text_frame",
            root=self.configFrame,
            corner_radius=12,
        ).withGridProperties(
            row=0, column=0, columnspan=2, padx=0, pady=(15, 0), sticky="new"
        )
        _cfgTextFrame.getInstance().grid_rowconfigure(0, weight=1)
        _cfgTextFrame.getInstance().grid_columnconfigure(0, weight=1)
        _cfgTextFrame.grid()
        configUI.add(
            ctk.CTkLabel,
            "cfg_text",
            root=_cfgTextFrame.getInstance(),
            text="LED Information (initial values):",
            font=(self.appRoot.FONT_NAME, 20, "bold"),
            justify="center",
        ).grid(row=0, column=0, padx=0, pady=(20, 0), sticky="new")
        configUI.add(
            ctk.CTkLabel,
            "cfg_text_info",
            root=_cfgTextFrame.getInstance(),
            text="""ok garmin""",
            font=(self.appRoot.FONT_NAME, 14),
            justify="left",
        ).grid(row=1, column=0, padx=(20, 0), pady=10, sticky="nw")

        configUI.add(
            ctk.CTkLabel,
            "brightness_label",
            root=self.configFrame,
            text="Brightness\n(Master)",
            font=(self.appRoot.FONT_NAME, 16),
        ).grid(row=1, column=0, padx=(20, 20), pady=(0, 20), sticky="nsw")
        configUI.add(
            ctk.CTkSlider,
            "brightness_slider",
            root=self.configFrame,
            from_=0,
            to=255,
            command=self.appRoot.leds.setBrightness,
            number_of_steps=256,
            width=300,
        ).grid(row=1, column=1, padx=(20, 20), pady=(0, 20), sticky="nsew")
        configUI.get("brightness_slider").getInstance().set(
            self.appRoot.leds.getBrightness()
        )

        """Segments Page"""
        # segmentsFrame = self.tabview.getInstance().tab("Segments")
        # self.segmentsUI = CommandUI(segmentsFrame)
        # segmentsFrame.grid_columnconfigure(0, weight=1)
        # segmentsFrame.grid_columnconfigure(1, weight=0)
        # segmentsFrame.grid_rowconfigure(0, weight=0)

        # self.segmentsUI.add(
        #     ctk.CTkLabel,
        #     "l_ab",
        #     text="Currently Selected Segment:",
        #     font=(self.appRoot.FONT_NAME, 20, "bold"),
        # ).grid(row=0, column=0, padx=(20, 0), pady=20, sticky="nw")
        # self.segmentsUI.add(
        #     ctk.CTkLabel,
        #     "segmentNo",
        #     textvariable=self.tv_segmentNum,
        #     font=(self.appRoot.FONT_NAME, 20),
        # ).grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nw")
        # _segmentsFrameOverlay = (
        #     self.segmentsUI.add(
        #         ctk.CTkFrame,
        #         "frame_overlay",
        #         corner_radius=12,
        #     )
        #     .grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        #     .getInstance()
        # )
        # _segmentsFrameOverlay.grid_columnconfigure(0, weight=1)
        # _segmentsFrameOverlay.grid_rowconfigure(0, weight=1)
        # self.segmentsUI.add(
        #     ctk.CTkSegmentedButton,
        #     "selector",
        #     root=_segmentsFrameOverlay,
        #     values=list(self.appRoot.leds.subStrips.keys()),
        #     corner_radius=12,
        #     height=40,
        # ).grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # self.segmentsUI.add(
        #     ctk.CTkButton,
        #     "selectall",
        #     root=_segmentsFrameOverlay,
        #     text="Select Whole Strip",
        #     font=(self.appRoot.FONT_NAME, 20),
        #     height=40,
        # ).grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    def _initCommands(self):
        def lockPage():
            self.tabviewUI.setFrame("main")
            self.ui.get("b_config").getInstance().configure(text="Configuration")
            self.ui.get("b_config").drop()

        self.appRoot.addLockCallback(lockPage)

        def showConfig():
            if self.tabviewUI.getCurrentFrameName() != "main":
                self.ui.get("b_config").getInstance().configure(text="Configuration")
                self.tabviewUI.setFrame("main")
            else:
                self.ui.get("b_config").getInstance().configure(text="Back to LEDs")
                self.tabviewUI.setFrame("config")

        self.ui.get("b_config").setCommand(showConfig)

        # def selector_callback(value):
        #     if value == -1:
        #         self.tv_segmentNum.set(-1)
        #         self.tv_segmentLabel.set("All")
        #         self.segmentsUI.get("selector").getInstance().set(-1)
        #         return
        #     for id, substrip in self.appRoot.leds.subStrips.items():
        #         if id == value:
        #             self.tv_segmentNum.set(substrip.rangeStr)
        #             self.tv_segmentLabel.set(id)
        #             break

        # self.segmentsUI.get("selector").setCommand(selector_callback)
        # self.segmentsUI.get("selectall").setCommand(lambda: selector_callback(-1))

        self.ui.get("color_picker").setCommand(
            lambda rgb: self.appRoot.leds.setColor(rgb, subStrip=self.tv_segmentNum.get() if self.tv_segmentNum.get() != -1 else None)
        )

    def onShow(self):
        if self.appRoot.hasFullAccess():
            self.ui.get("b_config").getInstance().configure(text="Configuration")
            self.ui.get("b_config").grid()

    def onHide(self):
        self.ui.get("b_config").getInstance().configure(text="Configuration")
        self.ui.get("b_config").drop()
        self.tabviewUI.setFrame("main")

    def addTheme(self, theme: "LEDTheme"):
        rowPos = self._loadedThemeCount // 2
        colPos = self._loadedThemeCount & 1  # will always be either col 0 or 1
        self._loadedThemeCount += 1

        # callback for a long pres
        def longPressFactory(loop: "LEDTheme"):
            def exception_wrapper():
                try:
                    # self.appRoot.setLoop(loop)
                    # self.navigator.navigateEphemeral(loop.getSettings(self.appRoot))
                    pass
                except:
                    self.ui.exceptionCallback(traceback.format_exc())

            return exception_wrapper

        # callback for a regular press
        def commandFactory(loop):
            def exception_wrapper():
                try:
                    self.appRoot.leds.setLoop(
                        loop.id,
                        subStrip=self.tv_segmentLabel.get(),
                    )
                except:
                    self.ui.exceptionCallback(traceback.format_exc())

            return exception_wrapper

        self.themesUI.add(
            QuackExtendedButton,
            f"b_{theme.id.lower()}",
            text=theme.friendlyName,
            compound="top",
            font=(self.appRoot.FONT_NAME, 20),
            # width=200,
            # height=150,
            border_spacing=8,
            border_width=0,
            corner_radius=20,
            image=ctk.CTkImage(Image.open(theme.imagePath), size=(200, 150)),
            command=commandFactory(theme),
            longpress_callback=longPressFactory(theme),
            longpress_threshold=450,
        ).grid(
            row=rowPos,
            column=colPos,
            padx=(5, 10),
            pady=(0, 40),
            stick="ne" if colPos else "nw",
        )

