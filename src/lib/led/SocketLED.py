import socket
import threading
import customtkinter as ctk


class SocketLED:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socketListenerFactory = lambda: threading.Thread(target=self._socket_listener, daemon=True)
        self.socketSendFactory = lambda: threading.Thread(target=self._socket_sender, daemon=True)

        self._sender = ctk.StringVar(value="")

        self._running = False

        self.onConnect = lambda: None
        self.onDisconnect = lambda: None
        self.exceptionCall = lambda e: print(f"Socket error: {e}")

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

        self.sock.close()

    def _socket_sender(self):
        self._running = True
        try:
            try:
                self.sock.connect(("127.0.0.1", 5000))
                self.onConnect()
            except Exception as e:
                self.exceptionCall(f"Error connecting to server: {e}")
            # self.socketListenerFactory().start()

            lastMsg = self._sender.get()
            while True:
                if self._sender.get() == lastMsg:
                    continue
                self.onConnect()
                lastMsg = self._sender.get()
                try:
                    self.sock.sendall(lastMsg.encode("utf-8"))
                except Exception as e:
                    self.exceptionCall(f"Error sending data: {e}")
        except Exception as e:
            self.exceptionCall(f"Error in socket sender: {e}")
        self.onDisconnect()
        self._running = False

    def begin(self):
        if self._running:
            return
        self.socketSendFactory().start()

    def numPixels(self):
        return 822
    
    def getBrightness(self):
        return 255

    def setLoop(self, loop: str, subStrip="All"):
        self._sender.set(f"set:{loop}")
        # self._subStrip = subStrip
