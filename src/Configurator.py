import json
import os
from lib.Themes import Theme

"""
Configurator class for managing application settings and configurations.
"""
class Configurator:
    _INSTANCE = None

    _SCHEMA_VER = 1

    def __init__(self, appName: str):
        self.settings = {
            "schema": self._SCHEMA_VER,
        }

        self._defaultSettings()
    
        if os.name == "nt":
            self._config_path = "./appconfig.json"
        else:
            self._config_path = os.path.expanduser(f"~/.config/{appName}/appconfig.json")
            if not os.path.exists(os.path.expanduser("~/.config")):
                os.makedirs(os.path.expanduser("~/.config"))
            if not os.path.exists(os.path.dirname(self._config_path)):
                os.makedirs(os.path.dirname(self._config_path))
            if not os.path.exists(self._config_path):
                with open(self._config_path, "w") as config_file:
                    json.dump(self.settings, config_file, indent=4)
        
        self.loadSettings()

    def loadSettings(self):
        try:
            with open(self._config_path, "r") as config_file:
                file_contents = json.load(config_file)
                if "schema" not in file_contents or file_contents["schema"] != self._SCHEMA_VER:
                    print(f"Configuration schema mismatch. Expected {self._SCHEMA_VER}, found {file_contents.get('schema', 'unknown')}. Using default settings.")
                    self._defaultSettings()
                    self.saveSettings()
                else:
                    self.settings = file_contents
        except FileNotFoundError:
            self.saveSettings()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self._config_path}. Using default settings.")

    def saveSettings(self):
        try:
            with open(self._config_path, "w") as config_file:
                json.dump(self.settings, config_file, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")
        
    def _defaultSettings(self):
        self.settings = {
            "schema": self._SCHEMA_VER,
            "appearance_mode": "dark",
            "theme": Theme.Cherry.value
        }

    def getAppearanceMode(self):
        return self.settings["appearance_mode"]
    def setAppearanceMode(self, mode: str):
        if mode.lower() in ["dark", "light", "system"]:
            self.settings["appearance_mode"] = mode.lower()
        else:
            raise ValueError("Invalid appearance mode. Choose from 'dark', 'light', or 'system'.")

    def getTheme(self):
        return self.settings["theme"]
    def setTheme(self, theme: Theme):
        self.settings["theme"] = theme.value

    @classmethod
    def getInstance(cls):
        if cls._INSTANCE is None:
            return None
        return cls._INSTANCE

    @classmethod
    def initialize(cls, appName: str):
        if cls._INSTANCE is None:
            cls._INSTANCE = Configurator(appName)
        return cls._INSTANCE
    
    @staticmethod
    def getSchemaVersion() -> int:
        return Configurator._SCHEMA_VER
