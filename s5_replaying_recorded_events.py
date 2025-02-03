import sys
import time
import pandas as pd

from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from misc import MOUSE_BUTTON_MAP, KEY_CODE_MAP


def convert_to_pynput_mouse_button(obs_button_code):
    """Convert a plugin’s mouse button code to pynput’s Button.*"""
    return MOUSE_BUTTON_MAP.get(int(obs_button_code), None)


def convert_to_pynput_key(obs_key_code):
    """Convert a plugin’s keycode to pynput’s Key.* or a raw character."""
    obs_key_code = int(obs_key_code)
    if obs_key_code in KEY_CODE_MAP:
        return KEY_CODE_MAP[obs_key_code]
    # If it's not in KEY_CODE_MAP, maybe it's a letter or digit scancode.
    # You could map raw scancodes to ASCII or skip unknown keys.
    return None


def replay_events(csv_path):
    df = pd.read_csv(csv_path)
    df = df.sort_values(by="time", ascending=True).reset_index(drop=True)

    mouse = MouseController()
    keyboard = KeyboardController()

    # move mouse to first event where event_type is mouse_moved
    for i in range(len(df)):
        row = df.loc[i]
        if row["event_type"] == "mouse_moved":
            mouse.position = (row["x"], row["y"])
            break

    if len(df) == 0:
        print("No events to replay.")
        return

    # We'll sleep according to deltas between consecutive events
    previous_time = df.loc[0, "time"]

    for i in range(len(df)):
        row = df.loc[i]
        t_current = row["time"]
        event_type = row["event_type"]

        if event_type == "mouse_moved":
            mouse.position = (row["x"], row["y"])

        elif event_type == "mouse_pressed":
            btn = convert_to_pynput_mouse_button(row["button"])
            if btn:
                print(f"Mouse pressed: {btn}")
                mouse.press(btn)
                time.sleep(0.01)

        elif event_type == "mouse_released":
            btn = convert_to_pynput_mouse_button(row["button"])
            if btn:
                print(f"Releasing mouse: {btn}")
                mouse.release(btn)

        elif event_type == "key_pressed":
            key_obj = convert_to_pynput_key(row["keycode"])
            if key_obj:
                print(f"Pressing key: {key_obj}")
                keyboard.press(key_obj)

        elif event_type == "key_released":
            key_obj = convert_to_pynput_key(row["keycode"])
            if key_obj:
                print(f"Releasing key: {key_obj}")
                keyboard.release(key_obj)

        # Sleep after performing the action
        dt = (t_current - previous_time) / 1000.0  # If 'time' is in ms
        if dt > 0:
            time.sleep(dt)

        previous_time = t_current


def main():
    # If you want a simple CLI usage: `python replay.py path_to_filtered.csv`
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Countdown so you can prepare (e.g., focus the correct window)
    print("Replaying events from:", csv_path)
    countdown = 5
    print(f"Starting in {countdown} seconds...")
    for i in range(countdown, 0, -1):
        print(i)
        time.sleep(1)

    print("Go!")
    replay_events(csv_path)
    print("Replay complete.")


if __name__ == "__main__":
    main()
