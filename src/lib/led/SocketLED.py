import socket
import threading
import time
import queue


class SocketLED:
    _instance = None

    def __init__(self):
        if SocketLED._instance is not None:
            raise RuntimeError(
                "SocketLED is a singleton and cannot be instantiated multiple times."
            )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socketListenerFactory = lambda: threading.Thread(
            target=self._socket_listener, daemon=True
        )
        self.socketSendFactory = lambda: threading.Thread(
            target=self._socket_sender, daemon=True
        )

        self._sender = queue.Queue()

        self._running = False

        self.onConnect = lambda: None
        self.onDisconnect = lambda: None
        self.exceptionCall = lambda e: print(f"Socket error: {e}")

        self._listenCallbackMap = {
            "current:": [],
            "themes:": [],
        }

    def _handle_message(self, message: str):
        if message.startswith("current:"):
            theme = message[len("current:"):].strip()
            for callback in self._listenCallbackMap["current:"]:
                callback(theme)
            self._listenCallbackMap["current:"].clear()
        elif message.startswith("themes:"):
            themes_str = message[len("themes:"):].strip()
            themes = themes_str.split(",") if themes_str else []
            for callback in self._listenCallbackMap["themes:"]:
                callback(themes)
            self._listenCallbackMap["themes:"].clear()
        else:
            self.exceptionCall(f"UKN-MSG->{message}")

    def _socket_listener(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self._handle_message(data.decode("utf-8"))
            except Exception as e:
                self.exceptionCall(f"Error receiving data: {e}")
                break

    def _socket_sender(self):
        self._running = True
        try:
            try:
                # Recreate the socket before each connection attempt
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(("127.0.0.1", 5000))
                self.onConnect()
            except Exception as e:
                self.onDisconnect()
                self.exceptionCall(f"Error connecting to server: {e}")
                self._running = False
                return
            self.socketListenerFactory().start()

            while True:
                time.sleep(0.005)
                try:
                    msg = self._sender.get()
                except Exception as e:
                    self.exceptionCall(f"Error getting message from queue: {e}")
                    continue

                # normalize None -> ignore
                if msg is None:
                    continue

                if msg == "disconnect":
                    try:
                        self.sock.close()
                    except Exception as e:
                        self.exceptionCall(f"Error closing socket: {e}")
                    break

                try:
                    # ensure the message is a bytes-like object
                    self.sock.sendall(str(msg).encode("utf-8"))
                except Exception as e:
                    self.exceptionCall(f"Error sending data: {e}")
        except Exception as e:
            self.exceptionCall(f"Error in socket sender: {e}")
        self.onDisconnect()
        self._running = False
        del self.sock

    def begin(self):
        if self._running:
            return
        self.exceptionCall("Starting socket.")
        self.socketSendFactory().start()

    def numPixels(self):
        return 822

    def getBrightness(self):
        return 255

    def getCurrentTheme(self, callback):
        self._listenCallbackMap["current:"].append(callback)
        self._sender.put("get:")
    
    def getThemes(self, callback):
        self._listenCallbackMap["themes:"].append(callback)
        self._sender.put("list:")

    def setLoop(self, loop: str, subStrip="All"):
        self._sender.put(f"set:{loop}")
        # self._subStrip = subStrip
    
    def setAttribute(self, key: str, value: str):
        self._sender.put(f"attr:{key},{value}")

    def setBrightness(self, brightness: int):
        brightness = int(brightness)
        brightness &= 0xFF
        self._sender.put(f"bright:{brightness}")

    def setColor(self, color: tuple, subStrip="All"):
        self._sender.put(f"colorrgb:{color[0]},{color[1]},{color[2]}")

    def off(self):
        self._sender.put(f"noloop")

    def disconnect(self):
        self._sender.put("disconnect")

    def killServer(self):
        self._sender.put(f"end")

    @classmethod
    def getInstance(cls):
        return cls._instance
