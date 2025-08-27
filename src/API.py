import flask
import threading

class QuackDEAPI:
    def __init__(self):
        self.base_url = "127.0.0.1"
        self.port = 5000

        self._api_thread = None

    def start_server(self):
        app = flask.Flask(__name__)

        @app.route("/api/quack", methods=["GET"])
        def quack():
            return {"message": "Quack!"}

        app.run(host=self.base_url, port=self.port)
    
    def init(self):
        assert self._api_thread is None, "API server is already running"
        self._api_thread = threading.Thread(target=self.start_server, daemon=True)
        self._api_thread.start()
