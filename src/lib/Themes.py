import customtkinter as ctk
import enum


class Theme(enum.Enum):
    AUTUMN = "./assets/themes/autumn.json"
    BREEZE = "./assets/themes/breeze.json"
    CHERRY = "./assets/themes/cherry.json"
    EFFOC = "./assets/themes/effoc.json"
    MARSH = "./assets/themes/marsh.json"
    MIDNIGHT = "./assets/themes/midnight.json"
    ROSE = "./assets/themes/rose.json"

    @classmethod
    def getThemeNames(cls):
        return [theme.name for theme in cls]
