import asyncio
import subprocess
import base64
import websockets
import sys

# Constants
VIDEO_PORT = 8765

async def stream_video(websocket, path):
    """
    Server: Captures screen via FFmpeg and streams it over WebSockets.
    """
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "x11grab",  # Change this for different OS
        "-video_size", "1280x720",
        "-framerate", "30",
        "-i", ":0.0",
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-f", "mpegts",
        "pipe:1"
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    try:
        while True:
            chunk = proc.stdout.read(4096)
            if not chunk:
                break

            # Send raw binary frames
            await websocket.send(chunk)

    finally:
        proc.terminate()
        await websocket.close()

async def receive_video(server_ip):
    """
    Client: Receives video over WebSockets and pipes it into FFplay.
    """
    ffplay_cmd = [
        "ffplay",
        "-i", "pipe:0",
        "-autoexit",
        "-nostats",
        "-loglevel", "quiet"
    ]
    ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE)

    async with websockets.connect(f"ws://{server_ip}:{VIDEO_PORT}") as ws:
        print(f"Connected to server at ws://{server_ip}:{VIDEO_PORT}")

        try:
            async for message in ws:
                ffplay_proc.stdin.write(message)
                ffplay_proc.stdin.flush()
        finally:
            ffplay_proc.stdin.close()
            ffplay_proc.terminate()

async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Server: python stream.py server")
        print("  Client: python stream.py client SERVER_IP")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "server":
        print(f"Starting video server on ws://0.0.0.0:{VIDEO_PORT}")
        async with websockets.serve(stream_video, "0.0.0.0", VIDEO_PORT):
            await asyncio.Future()  # Keep server running

    elif mode == "client":
        if len(sys.argv) < 3:
            print("Usage: python stream.py client SERVER_IP")
            sys.exit(1)

        server_ip = sys.argv[2]
        await receive_video(server_ip)

    else:
        print("Invalid mode. Use 'server' or 'client'.")

if __name__ == "__main__":
    asyncio.run(main())
