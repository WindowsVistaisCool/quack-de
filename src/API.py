import flask

class QuackDEAPI:
    def __init__(self):
        self.base_url = "127.0.0.1"
        self.port = 5000

    def start_server(self):
        app = flask.Flask(__name__)

        @app.route("/api/quack", methods=["GET"])
        def quack():
            return {"message": "Quack!"}

        app.run(host=self.base_url, port=self.port)

    