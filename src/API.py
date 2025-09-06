import flask
import threading

from lib.led.SocketLED import SocketLED


class QuackDEAPI:
    def __init__(self, leds: "SocketLED"):
        self.base_url = "0.0.0.0"
        self.port = 6000

        self.leds = leds

        self._api_thread = None

    def start_server(self):
        app = flask.Flask(__name__)

        @app.route("/api/quack", methods=["GET"])
        def quack():
            return {"message": "Quack!"}
        
        @app.route("/api/themes/set", methods=["POST"])
        def set_theme():
            new_theme = flask.request.json.get("theme")
            if new_theme:
                self.leds.setLoop(new_theme)
                return {"message": f"Theme set to {new_theme}"}
            return {"error": "No theme provided"}, 400

        app.run(host=self.base_url, port=self.port)
    
    def init(self):
        assert self._api_thread is None, "API server is already running"
        self._api_thread = threading.Thread(target=self.start_server, daemon=True)
        self._api_thread.start()
