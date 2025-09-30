from lib.Configurator import Configurator
from lib.QuackApp import QuackApp
from lib.led.LEDThemeSettings import LEDThemeSettings

class LEDTheme:
    def __init__(self,
            id: str,
            settingsUIFactory: callable = None,
            *,
            imagePath: str = "assets/images/missing.png",
            friendlyName: str = None,
        ):
        self.id = id
        self.settingUIFactory = settingsUIFactory
        self.imagePath = imagePath
        self.friendlyName = friendlyName or self.id

        self.themeData = Configurator.getInstance().get(self.id, {})

        self.app: 'QuackApp' = None

    def getSettings(self, app: QuackApp) -> 'LEDThemeSettings':
        """
        Returns the settings page associated with this LED loop.
        """
        if not app:
            app = self.app
        else:
            assert isinstance(app, QuackApp), "app must be an instance of QuackApp"
        return LEDThemeSettings(app, self, uiFactory=self.settingUIFactory)
    
    def getData(self) -> dict:
        return self.themeData

    def setData(self, key, value):
        """
        Sets a value in the LED theme data.
        """
        self.themeData[key] = value

    def saveData(self, data: dict=None):
        if not data:
            data = self.getData()
        Configurator.getInstance().set(self.id, data)
        Configurator.getInstance().saveSettings()
