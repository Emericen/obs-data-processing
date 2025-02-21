import io
import time
import base64
from PIL import ImageGrab
from tqdm import tqdm


if __name__ == "__main__":
    resolutions = [
        (1280, 720),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160),
    ]

    frame_count = 1000
    start_time = time.time()
    total_bytes = 0
    frame_stats = []

    for width, height in resolutions:
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
