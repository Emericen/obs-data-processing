import sys
import argparse
from threading import Thread

import socket
from websocket import WebSocketApp
from websocket_server import WebsocketServer

from pynput import mouse, keyboard


class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip


class Server(Node):
    def __init__(self, host="0.0.0.0", port=8765):
        super().__init__(host, port)
        self.server = WebsocketServer(self.host, self.port)
        self._setup_handlers()

    def _setup_handlers(self):
        self.server.set_fn_new_client(self._new_client)
        self.server.set_fn_client_left(self._client_left)
        self.server.set_fn_message_received(self._message_received)

    def _new_client(self, client, server):
        print(f"New client connected: {client['address']}")

    def _client_left(self, client, server):
        print(f"Client disconnected: {client['address']}")

    def _message_received(self, client, server, message):
        print(f"\nReceived: {message}")
        sys.stdout.write("> ")
        sys.stdout.flush()

    def start(self):
        print(f"Server started on {self.host}:{self.port}")
        try:
            self.server.run_forever()
        except KeyboardInterrupt:
            self.server.shutdown()


class Client(Node):
    def __init__(self, server_ip, port=8765):
        super().__init__(server_ip, port)
        self.ws = None
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_keyboard_press,
            on_release=self._on_keyboard_release,
        )

    def start(self):
        uri = f"ws://{self.host}:{self.port}"
        self.ws = WebSocketApp(
            uri,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.ws.run_forever()

    
    def _on_message(self, ws, message):
        print(f"\nReceived: {message}")

    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws, close_status_code, close_msg):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        print("Connection closed")

    def _on_open(self, ws):
        print("Connected to server")
        Thread(target=self._send_messages, daemon=True).start()

    def _send_messages(self):
        while True:
            message = input("> ")
            self.ws.send(message)

    def _on_mouse_move(self, x, y):
        if self.ws:
            self.ws.send(f"mouse_move {x}, {y}")

    def _on_mouse_click(self, x, y, button, pressed):
        if self.ws:
            self.ws.send(f"mouse_click {x}, {y}, {button}, {pressed}")

    def _on_mouse_scroll(self, x, y, dx, dy):
        if self.ws:
            self.ws.send(f"mouse_scroll {x}, {y}, {dx}, {dy}")

    def _on_keyboard_press(self, key):
        if self.ws:
            self.ws.send(f"keyboard_press {key}")

    def _on_keyboard_release(self, key):
        if self.ws:
            self.ws.send(f"keyboard_release {key}")


def main():
    """
    Server:
        python s6_io_test_nodes.py --mode server

    Client:
        python s6_io_test_nodes.py --mode client --ip SERVER_IP
    """
    parser = argparse.ArgumentParser(description="WebSocket Node")
    parser.add_argument(
        "--mode", choices=["server", "client"], help="Run as server or client"
    )
    parser.add_argument("--ip", help="Server IP address (for client mode)")
    parser.add_argument(
        "--port", type=int, default=8765, help="Port number (default: 8765)"
    )

    args = parser.parse_args()

    if not args.mode:
        args.mode = input("Choose mode (server/client): ").lower()

    local_ip = Node.get_local_ip()
    print(f"Local IP: {local_ip}")

    if args.mode == "server":
        node = Server(host="0.0.0.0", port=args.port)
    else:
        if not args.ip:
            args.ip = input("Enter server IP address: ")
        node = Client(server_ip=args.ip, port=args.port)

    node.start()


if __name__ == "__main__":
    main()
