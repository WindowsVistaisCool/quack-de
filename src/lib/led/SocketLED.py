import socket
import threading
import customtkinter as ctk

from lib.led.LEDTheme import LEDTheme


class SocketLED:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socketListenerFactory = lambda: threading.Thread(target=self._socket_listener, daemon=True)
        self.socketSendFactory = lambda: threading.Thread(target=self._socket_sender, daemon=True)

        self._sender = ctk.StringVar(value="")

    def _socket_listener(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self._handle_message(data.decode("utf-8"))
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

        self.sock.close()

    def _socket_sender(self):
        try:
            self.sock.connect(("127.0.0.1", 5000))
        except Exception as e:
            print(f"Error connecting to server: {e}")
        self.socketListenerFactory().start()

        lastMsg = self._sender.get()
        while True:
            if self._sender.get() == lastMsg:
                continue
            lastMsg = self._sender.get()
            try:
                self.sock.sendall(lastMsg.encode("utf-8"))
            except Exception as e:
                print(f"Error sending data: {e}")

    def begin(self):
        self.socketSendFactory().start()

    def numPixels(self):
        return 822
    
    def getBrightness(self):
        return 255

    def setLoop(self, loop: str, subStrip="All"):
        self._sender.set(f"set:{loop}")
        # self._subStrip = subStrip
