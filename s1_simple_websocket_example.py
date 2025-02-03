import websocket

# Define callback functions
def on_message(ws, message):
	print(message)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

# Connect to OBS's WebSocket server
ws = websocket.WebSocketApp(
    "ws://localhost:16899", # <-- OBS plugin port
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.on_open = on_open
ws.run_forever()