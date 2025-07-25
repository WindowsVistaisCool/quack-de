import customtkinter as ctk
import enum

class Theme(enum.Enum):
    Cherry = "./assets/themes/cherry.json"
    Midnight = "./assets/themes/midnight.json"
    Metal = "./assets/themes/metal.json"
    Sky = "./assets/themes/sky.json"
    Violet = "./assets/themes/violet.json"
    Yellow = "./assets/themes/yellow.json"

    @classmethod
    def getThemeNames(cls):
        return [theme.name for theme in cls]

