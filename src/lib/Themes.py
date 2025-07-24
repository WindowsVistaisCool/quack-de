import customtkinter as ctk
import enum

class Theme(enum.Enum):
    Cherry = "./themes/cherry.json"
    Metal = "./themes/metal.json"
    Sky = "./themes/sky.json"
    Violet = "./themes/violet.json"
    Yellow = "./themes/yellow.json"

    @classmethod
    def getThemeNames(cls):
        return [theme.name for theme in cls]

