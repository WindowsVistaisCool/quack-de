import customtkinter as ctk
import enum

class Theme(enum.Enum):
    Cherry = "./themes/cherry.json"
    Violet = "./themes/violet.json"

    @classmethod
    def getThemeNames(cls):
        return [theme.name for theme in cls]

