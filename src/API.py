import flask
import threading
import time
from lib.led.SocketLED import SocketLED


class QuackDEAPI:
    def __init__(self, leds: "SocketLED"):
        self.base_url = "0.0.0.0"
        self.port = 6000

        self.leds: SocketLED = leds

        self._api_thread = None

    def start_server(self):
        app = flask.Flask(__name__)

        @app.route("/api/themes/current", methods=["GET"])
        def get_theme():
            themeReturn = None
            def callback(theme):
                nonlocal themeReturn
                themeReturn = theme
            self.leds.getCurrentTheme(callback)
            for _ in range(50):
                if themeReturn is not None:
                    return {"theme": themeReturn}
                time.sleep(0.1)
            return {"error": "Timeout fetching theme"}, 500

        @app.route("/api/themes/list", methods=["GET"])
        def list_themes():
            themesReturn = []
            def callback(themes):
                nonlocal themesReturn
                themesReturn = themes
            self.leds.getThemes(callback)
            for _ in range(50):
                if themesReturn:
                    return {"themes": themesReturn}
                time.sleep(0.1)
            return {"error": "Timeout fetching themes"}, 500

        @app.route("/api/themes/set", methods=["POST"])
        def set_theme():
            new_theme = flask.request.json.get("theme")
            if new_theme:
                self.leds.setLoop(new_theme)
                return {"message": f"Theme set to {new_theme}"}
            return {"error": "No theme provided"}, 400

        @app.route("/api/off", methods=["POST"])
        def set_off():
            self.leds.off()
            return {"message": "LEDs turned off"}
        
        @app.route("/api/brightness", methods=["POST"])
        def set_brightness():
            brightness = flask.request.json.get("brightness")
            if brightness is not None:
                self.leds.setBrightness(brightness)
                return {"message": f"Brightness set to {brightness}"}
            return {"error": "No brightness value provided"}, 400

        app.run(host=self.base_url, port=self.port)
    
    def init(self):
        assert self._api_thread is None, "API server is already running"
        self._api_thread = threading.Thread(target=self.start_server, daemon=True)
        self._api_thread.start()
