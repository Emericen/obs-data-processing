import os
import time
import json
import websocket
import threading
import obspython as obs


recording_client = None
streaming_client = None


def script_description():
    return (
        "Records M&K events via OBS WebSocket on start/stop of streaming or recording."
    )


def script_load(settings):
    # Called once when the script is loaded
    obs.obs_frontend_add_event_callback(on_event)
    print("Hello! Script loaded successfully!")


def script_unload():
    # Called once when the script is unloaded
    print("Goodbye! Script unloaded!")
    global recording_client, streaming_client
    # Clean up any ongoing connections
    if recording_client:
        recording_client.stop()
    if streaming_client:
        streaming_client.stop()


def get_output_path():
    # Try to get OBS recording path first
    output_dir = obs.obs_frontend_get_current_record_output_path()
    if not output_dir:
        # Fallback to Documents folder if we can't get OBS path
        output_dir = os.path.join(os.path.expanduser("~"), "Documents")

    # Create filename with timestamp
    filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    return os.path.join(output_dir, filename)


def on_event(event):
    """
    Called whenever an OBS frontend event occurs, e.g. start/stop recording/streaming.
    We use this to start/stop our OBSClient (websocket listener).
    """
    global recording_client, streaming_client

    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTING:
        print("🎥 Recording is starting...")
        output_path = get_output_path()
        recording_client = OBSClient(port=16899, output_path=output_path)
        recording_client.start()
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        print("🎥 Recording has started!")
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPING:
        print("🛑 Recording is stopping...")
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        print("🛑 Recording has stopped!")
        if recording_client:
            recording_client.stop()
            recording_client = None
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTING:
        print("📡 Streaming is starting...")
        if not streaming_client:
            output_path = f"streaming_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            streaming_client = OBSClient(port=16899, output_path=output_path)
            streaming_client.start()
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        print("📡 Streaming has started!")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPING:
        print("🔴 Streaming is stopping...")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        print("🔴 Streaming has stopped!")
        if streaming_client:
            streaming_client.stop()
            streaming_client = None


class EventWriter:
    def __init__(self, csv_path: str):
        self._csv_file = open(csv_path, "w", newline="")
        # Write header
        columns = [
            "time",  # Seconds since recording started
            "event_source",  # Source of the input
            "event_type",  # Type of event
            "x",  # Mouse X coordinate
            "y",  # Mouse Y coordinate
            "button",  # Mouse button number
            "clicks",  # Number of clicks
            "keycode",  # Keyboard key code
            "rawcode",  # Raw key code
            "char",  # Character (for key_typed)
            "mask",  # Event mask
            "wheel_amount",  # Wheel scroll amount
            "wheel_direction",  # Wheel scroll direction
            "wheel_rotation",  # Wheel rotation value
        ]
        self._csv_file.write(",".join(columns) + "\n")
        self._csv_file.flush()

    def write(self, event_json: str):
        try:
            event = json.loads(event_json)
            values = [
                str(event.get("time", "")),
                event.get("event_source", ""),
                event.get("event_type", ""),
                str(event.get("x", "")),
                str(event.get("y", "")),
                str(event.get("button", "")),
                str(event.get("clicks", "")),
                str(event.get("keycode", "")),
                str(event.get("rawcode", "")),
                str(event.get("char", "")),
                str(event.get("mask", "")),
                str(event.get("wheel_amount", "")),
                str(event.get("wheel_direction", "")),
                str(event.get("wheel_rotation", "")),
            ]

            line = ",".join(values) + "\n"
            self._csv_file.write(line)
            self._csv_file.flush()

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error writing event: {e}")

    def close(self):
        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None


class OBSClient:
    def __init__(self, port: int, output_path: str):
        self.ws = websocket.WebSocketApp(
            f"ws://localhost:{port}/",
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws_thread = None
        self.event_writer = EventWriter(output_path)
        self.running = False

    def start(self):
        self.running = True
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()
        if self.event_writer:
            self.event_writer.close()

    def _on_open(self, ws):
        print("############# WebSocket Connection Opened ##############")

    def _on_message(self, ws, message):
        if self.running:
            self.event_writer.write(message)

    def _on_close(self, ws, close_status_code, close_msg):
        print("############# WebSocket Connection Closed ##############")

    def _on_error(self, ws, error):
        print(f"############# WebSocket Error ##############\n{error}")
