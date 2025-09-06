import socket
import threading
import time
import queue


class SocketLED:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socketListenerFactory = lambda: threading.Thread(target=self._socket_listener, daemon=True)
        self.socketSendFactory = lambda: threading.Thread(target=self._socket_sender, daemon=True)

        # use a thread-safe queue for outgoing messages instead of a UI StringVar
        # producer threads / callers call `put(...)`, the sender thread `get()`s
        self._sender = queue.Queue()

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
                # Recreate the socket before each connection attempt
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(("127.0.0.1", 5000))
                self.onConnect()
            except Exception as e:
                self.onDisconnect()
                self.exceptionCall(f"Error connecting to server: {e}")
                self._running = False
                return
            # self.socketListenerFactory().start()

            # Wait for messages from the queue and send them as they arrive.
            # queue.Queue.get() blocks until an item is available which avoids
            # busy-waiting and removes the need for a StringVar polling trick.
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

    def setLoop(self, loop: str, subStrip="All"):
        self._sender.put(f"set:{loop}")
        # self._subStrip = subStrip
    
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
