import sys
import argparse
from threading import Thread
import socket
from websocket import WebSocketApp
from websocket_server import WebsocketServer

from pynput import mouse, keyboard
from PIL import ImageGrab, Image
import io
import time
import base64
from tqdm import tqdm


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
        self.resolutions = [
            (1280, 720),   # 720p
            (1920, 1080),  # 1080p
            (2560, 1440),  # 1440p
            (3840, 2160),  # 2160p
        ]
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
        if message == "start":
            for width, height in self.resolutions:
                print(f"\nTesting {width}x{height}")
                region = (0, 0, width, height)
                frame_count = 1000
                start_time = time.time()
                total_bytes = 0
                frame_stats = []
                with tqdm(total=frame_count, desc="Capturing frames") as pbar:
                    for i in range(frame_count):
                        frame_start = time.time()
                        img = ImageGrab.grab(bbox=region)
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=50)
                        frame_data = base64.b64encode(buf.getvalue()).decode("utf-8")
                        self.server.send_message(client, frame_data)
                        frame_time = time.time() - frame_start
                        frame_stats.append(
                            {"bytes": len(frame_data), "time_ms": frame_time * 1000}
                        )
                        total_bytes += len(frame_data)
                        pbar.update(1)

                duration = time.time() - start_time
                times = [s["time_ms"] for s in frame_stats]
                sizes = [s["bytes"] for s in frame_stats]
                print(
                    f"\nFrame timing (ms): min={min(times):.1f}, max={max(times):.1f}, mean={sum(times)/len(times):.1f}"
                )
                print(
                    f"Frame sizes (bytes): min={min(sizes)}, max={max(sizes)}, mean={sum(sizes)/len(sizes):.1f}"
                )
                print(
                    f"Performance: {frame_count/duration:.1f} avg fps, {total_bytes/1024/1024/duration:.1f} avg MB/s"
                )

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
        self.frames_received = 0
        self.total_bytes = 0
        self.start_time = None

    def start(self):
        uri = f"ws://{self.host}:{self.port}"
        self.ws = WebSocketApp(
            uri,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws.run_forever()

    def _on_message(self, ws, message):
        if len(message) > 100:  # Likely base64 image data
            try:
                img_data = base64.b64decode(message)
                self.frames_received += 1
                self.total_bytes += len(img_data)
                if self.start_time is None:
                    self.start_time = time.time()
            except Exception as e:
                print("[CLIENT] Failed to decode image:", e)
        else:
            print(f"\n[CLIENT] Received text: {message}")

    def _on_error(self, ws, error):
        print("[CLIENT] WebSocket error:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("[CLIENT] Connection closed")

    def _on_open(self, ws):
        print("[CLIENT] Connected to server")
        Thread(target=self._send_messages, daemon=True).start()

    def _send_messages(self):
        """Continuously read user input from stdin and send to server."""
        while True:
            message = input("> ")
            self.ws.send(message)


def main():
    """
    Usage:
        Server: python s7_stream_nodes.py --mode server
        Client: python s7_stream_nodes.py --mode client --ip <SERVER_IP>
    """
    import argparse

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
