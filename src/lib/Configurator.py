from lib.Themes import Theme

"""
Configurator class for managing application settings and configurations.

TODO: implement lol
"""
class Configurator:
    _INSTANCE = None

    def __init__(self):
        self.appearance_mode = "dark"
        self.theme = Theme.Sky

    def getAppearanceMode(self):
        return self.appearance_mode

    def getTheme(self):
        return self.theme

    def setTheme(self, theme: Theme):
        self.theme = theme

    @classmethod
    def getInstance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE
