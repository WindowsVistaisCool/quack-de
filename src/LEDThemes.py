import customtkinter as ctk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.led.SocketLED import SocketLED


from lib.CommandUI import CommandUI
from lib.SwappableUI import SwappableUI
from lib.led.LEDTheme import LEDTheme
from lib.led.SocketLED import SocketLED

class LEDThemes:
    _instance = None

    def __init__(self, leds: SocketLED = None):
        assert LEDThemes._instance is None, "LEDThemes instance already exists"
        LEDThemes._instance = self
        self.leds = leds
        self.themes = {
            "null": LEDThemes.null()
        }  # needs to init like this because `self._checkLoopExists` references it
        self.themes = {
            # "ledSelector": self.ledSelector(),
            "rainbow": self.rainbow(),
            "fire2012": self.fire2012(),
            "rgbSnake": self.rgbSnake(),
            "twinkle": self.twinkle(),
            "pacifica": self.pacifica(),
            "epilepsy": LEDTheme("epilepsy"),
            "freaky": LEDTheme("freaky"),
        }

    @classmethod
    def _checkAssr(cls):
        """
        Check if the LEDThemes instance is initialized.
        Raises an AssertionError if not initialized.
        """
        assert cls._instance, "LEDThemes instance not initialized"

    @classmethod
    def getInstance(cls):
        cls._checkAssr()
        return cls._instance

    @classmethod
    def getTheme(cls, loop_id: str = None):
        cls._checkAssr()
        return cls._instance.themes.get(loop_id)

    @classmethod
    def getAllThemes(cls):
        cls._checkAssr()
        return cls._instance.themes.values()

    @staticmethod
    def null():
        return LEDTheme("null")

    def _checkThemeExists(self, theme_id: str):
        assert (
            theme_id not in self.themes.keys()
        ), f"LED theme '{theme_id}' already exists"

    # def ledSelector(self):
    #     self._checkThemeExists("ledSelector")

    #     num = ctk.IntVar(value=0)

    #     def uiMaker(theme: "LEDTheme", ui: CommandUI, withShowSaveButton: callable):
    #         ui.add(
    #             ctk.CTkLabel,
    #             "l_num",
    #             textvariable=num,
    #             font=("Arial", 20),
    #         ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
    #         ui.add(
    #             ctk.CTkSlider,
    #             "s_num",
    #             variable=num,
    #             from_=0,
    #             to=theme.leds.numPixels() - 1,
    #             number_of_steps=theme.leds.numPixels() - 2,
    #             height=30,
    #         ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
    #             lambda *_: self.leds.setAttribute("num", num.get())
    #             # withShowSaveButton(
    #             #     lambda *_: theme.setData("num", num.get())
    #             # )
    #         )

    #     return LEDTheme(
    #         "ledSelector",
    #         settingsUIFactory=uiMaker
    #     )

    def rainbow(self, *, _name="rainbow"):
        self._checkThemeExists(_name)

        iterations = ctk.IntVar(value=10)
        delay = ctk.IntVar(value=30)
        step_size = ctk.IntVar(value=4)

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            ui.add(
                ctk.CTkLabel,
                "l_iterations",
                text="Pattern Sparseness",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_iterations",
                variable=iterations,
                from_=1,
                to=100,
                number_of_steps=99,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("iterations", iterations.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("iterations", iterations.get())
                # )
            )
            ui.add(
                ctk.CTkLabel,
                "l_stepSize",
                text="Step Size",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_step_size",
                variable=step_size,
                from_=1,
                to=32,
                number_of_steps=31,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("stepSize", step_size.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("stepSize", step_size.get())
                # )
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/rainbow.png",
            friendlyName="Rainbow",
        )

    def fire2012(self, *, _name="fire2012"):
        self._checkThemeExists(_name)

        cooling = ctk.IntVar(value=30)
        sparking = ctk.IntVar(value=130)
        reversed = ctk.BooleanVar(value=False)

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            nonlocal self

            ui.add(ctk.CTkLabel, "l_cooling", text="Cooling", font=("Arial", 20)).grid(
                row=0, column=0, padx=20, pady=15, sticky="nsw"
            )
            ui.add(
                ctk.CTkSlider,
                "s_cooling",
                variable=cooling,
                from_=0,
                to=255,
                number_of_steps=254,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("cooling", cooling.get())
                # withShowSaveButton(lambda *_: theme.setData("cooling", cooling.get()))
            )

            ui.add(
                ctk.CTkLabel, "l_sparking", text="Sparking", font=("Arial", 20)
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_sparking",
                variable=sparking,
                from_=0,
                to=255,
                number_of_steps=254,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("sparking", sparking.get())
                # withShowSaveButton(lambda *_: theme.setData("sparking", sparking.get()))
            )

            ui.add(
                ctk.CTkCheckBox,
                "c_reversed",
                variable=reversed,
                text="Reverse",
            ).grid(
                row=2, columnspan=2, padx=(20, 20), pady=(0, 15), sticky="nsew"
            ).setCommand(
                lambda *_: self.leds.setAttribute("reversed", reversed.get())
                # withShowSaveButton(lambda *_: theme.setData("reversed", reversed.get()))
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/fire.png",
            friendlyName="Fireplace",
        )

    def rgbSnake(self, *, _name="rgbSnake"):
        self._checkThemeExists(_name)

        tailScaleFactor = ctk.IntVar(value=250)
        step_size = ctk.IntVar(value=1)  # pixels to skip

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            ui.add(
                ctk.CTkLabel,
                "l_tailScaleFactor",
                text="Tail Length",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_tailScaleFactor",
                variable=tailScaleFactor,
                from_=0,
                to=255,
                number_of_steps=249,
                height=30,
            ).grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("tailScaleFactor", tailScaleFactor.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("tailScaleFactor", tailScaleFactor.get())
                # )
            )
            ui.add(
                ctk.CTkLabel,
                "l_step_size",
                text="Snake Speed",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=20, pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_step_size",
                variable=step_size,
                from_=1,
                to=7,
                number_of_steps=8,
                height=30,
            ).grid(row=1, column=1, padx=(0, 20), pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("stepSize", step_size.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("stepSize", step_size.get())
                # )
            )

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/snake.png",
            friendlyName="Color Snake",
        )

    def pacifica(self, *, _name="pacifica"):
        self._checkThemeExists(_name)

        return LEDTheme(
            _name,
            imagePath="assets/images/ocean.png",
            friendlyName="Ocean Blue",
        )

    def twinkle(self, *, _name="twinkle"):
        """
        [TODO] describe
        Originally wrote for Arduino but adapted for Python.
        """

        twinkleSpeed = ctk.IntVar(value=5)  # 1-8
        twinkleDensity = ctk.IntVar(value=4)  # 1-8
        secondsPerPallette = ctk.IntVar(value=60)  # seconds
        coolLikeIncandescent = ctk.BooleanVar(value=True)

        def uiMaker(theme: LEDTheme, ui: CommandUI, withShowSaveButton: callable):
            nonlocal twinkleSpeed, twinkleDensity, secondsPerPallette, coolLikeIncandescent
            nonlocal self
            # nonlocal palettes

            sui = SwappableUI(ui.master)
            sui.grid(row=0, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")
            f_sliders = sui.addFrame("sliders")
            f_sliders.grid_columnconfigure(0, weight=0)
            f_sliders.grid_columnconfigure(1, weight=1)
            ui.add(
                ctk.CTkLabel,
                "l_speed",
                root=f_sliders,
                text="Speed (1-8):",
                font=("Arial", 20),
            ).grid(row=0, column=0, padx=(0, 20), pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_speed",
                root=f_sliders,
                from_=1,
                to=8,
                number_of_steps=7,
                height=30,
                variable=twinkleSpeed,
            ).grid(row=0, column=1, padx=0, pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("twinkleSpeed", twinkleSpeed.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("twinkleSpeed", twinkleSpeed.get())
                # )
            )
            ui.add(
                ctk.CTkLabel,
                "l_density",
                root=f_sliders,
                text="Density (1-8):",
                font=("Arial", 20),
            ).grid(row=1, column=0, padx=(0, 20), pady=15, sticky="nsw")
            ui.add(
                ctk.CTkSlider,
                "s_density",
                root=f_sliders,
                from_=1,
                to=8,
                number_of_steps=7,
                height=30,
                variable=twinkleDensity,
            ).grid(row=1, column=1, padx=0, pady=15, sticky="nsew").setCommand(
                lambda *_: self.leds.setAttribute("twinkleDensity", twinkleDensity.get())
                # withShowSaveButton(
                #     lambda *_: theme.setData("twinkleDensity", twinkleDensity.get())
                # )
            )
            
            # ui.add(
            #     ctk.CTkButton,
            #     "b_palettes",
            #     root=f_sliders,
            #     text="Palettes",
            #     command=lambda: sui.setFrame("palettes"),
            # ).grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="nsew")

            f_palettes = sui.addFrame("palettes")
            # ui.add(
            #     ctk.CTkButton,
            #     "b_back",
            #     root=f_palettes,
            #     text="Back",
            #     command=lambda: sui.setFrame("sliders"),
            # ).grid(row=0, column=0, padx=20, pady=15, sticky="nsew")
            # ui.add(
            #     ctk.CTkButton,
            #     "b_add_random",
            #     root=f_palettes,
            #     text="Add Random Palette",
            #     command=lambda: (
            #         palettes.append(
            #             Palette(
            #                 "Random Palette",
            #                 palette=[
            #                     ((r << 16) & 0xFF | (g << 8) & 0xFF | b & 0xFF)
            #                     for (r, g, b) in [
            #                         FastLEDFunctions.fromHSV(
            #                             random.randint(0, 255),  # hue
            #                             random.randint(
            #                                 220, 255
            #                             ),  # saturation (avoid white)
            #                             random.randint(160, 220),  # value (avoid black)
            #                         )
            #                         for _ in range(4)
            #                     ]
            #                 ]
            #                 * 4,
            #             ),
            #         ),
            #         theme._initTarget(theme, True),
            #     ),
            # ).grid(row=1, column=0, padx=20, pady=15, sticky="nsew")
            # ui.add(
            #     ctk.CTkButton,
            #     "b_clear",
            #     root=f_palettes,
            #     text="Clear Palettes",
            #     command=lambda: (
            #         palettes.clear(),
            #         theme._initTarget(theme, True),
            #     ),
            # ).grid(row=2, column=0, padx=20, pady=15, sticky="nsew")

            sui.setFrame("sliders")

        return LEDTheme(
            _name,
            settingsUIFactory=uiMaker,
            imagePath="assets/images/christmas.png",
            friendlyName="Christmas",
        )


class Palette:
    def __init__(self, name, colors=[], palette=None):
        self.name = name
        self.colors = colors
        self.palette = []

        if colors != [] and palette:
            self.palette = [self.colors[i] for i in palette]
        elif colors == []:
            self.palette = palette if palette else []

    def get(self):
        return tuple(self.palette)
