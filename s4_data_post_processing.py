import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
import argparse


def bin_and_filter_events(df: pd.DataFrame, bin_size: int = 16) -> pd.DataFrame:
    """
    Bucket events by `time // bin_size` and filter them:
      - Keep only the last mouse_moved event in each bin.
      - Keep press/release events in order, ignoring repeated presses/releases that are invalid
        (e.g., pressing a key that's already pressed).
    """
    # Ensure data is sorted by time
    df = df.sort_values(by="time").reset_index(drop=True)

    # Create a "bin" column
    df["time_bin"] = df["time"] // bin_size

    pressed_keys = set()
    result_rows = []

    # We'll iterate bins in ascending order
    for time_bin, group in tqdm(
        df.groupby("time_bin", sort=True),
        desc="Processing time bins",
        total=len(df["time_bin"].unique()),
    ):
        group = group.sort_values("time")

        # Track the final mouse position in this bin
        mouse_events = group[group["event_type"] == "mouse_moved"]
        final_mouse_row = None
        if not mouse_events.empty:
            final_mouse_row = mouse_events.iloc[-1].copy()

        # Process press/release events in chronological order
        for _, row in group.iterrows():
            et = row["event_type"]

            # If it's not a press/release, skip here; we handle mouse_moved separately
            if ("pressed" not in et) and ("released" not in et):
                continue

            # Determine the key or button ID
            # For example, if row['keycode'] is not nan, that might be the keyboard. Otherwise use mouse button.
            if pd.notna(row["keycode"]):
                k = row["keycode"]
            else:
                k = row["button"]

            # Pressed
            if "pressed" in et:
                # Skip if already pressed
                if k in pressed_keys:
                    continue
                pressed_keys.add(k)
                # Keep the row
                result_rows.append(row.copy())

            # Released
            elif "released" in et:
                # Skip if it wasn't actually pressed
                if k not in pressed_keys:
                    continue
                pressed_keys.remove(k)
                # Keep the row
                result_rows.append(row.copy())

        # Finally add the last mouse_moved event if it exists
        if final_mouse_row is not None:
            result_rows.append(final_mouse_row)

    # Build the new DataFrame
    filtered_df = pd.DataFrame(result_rows).reset_index(drop=True)

    # Optionally sort by actual time again (so press/release events appear in time order
    # before the final mouse move, if that’s important to you):
    filtered_df = filtered_df.sort_values(by="time").reset_index(drop=True)

    # Drop the helper column
    filtered_df.drop(columns=["time_bin"], inplace=True)

    return filtered_df


def main():
    parser = argparse.ArgumentParser(
        description="Down sample recorded actions to ~60 FPS"
    )
    parser.add_argument(
        "input_csv", help="Path to the input CSV file with recorded actions"
    )
    parser.add_argument("output_csv", help="Path to save the down sampled CSV file")
    parser.add_argument(
        "--bin-size",
        type=int,
        default=16,
        help="Bin size in milliseconds (default: 16 for ~60 FPS)",
    )
    args = parser.parse_args()

    try:
        # Read input CSV
        print(f"Reading input file: {args.input_csv}")
        df = pd.read_csv(args.input_csv)

        # Pre-process: change mouse_dragged to mouse_moved, and remove mouse_clicked
        df["event_type"] = df["event_type"].replace("mouse_dragged", "mouse_moved")
        df = df[df["event_type"] != "mouse_clicked"]

        # Process the data
        print(f"Processing with bin size: {args.bin_size}ms")
        filtered = bin_and_filter_events(df, bin_size=args.bin_size)

        # Save results
        filtered.to_csv(args.output_csv, index=False)
        print(f"\nOriginal: {len(df)} rows")
        print(f"Filtered: {len(filtered)} rows")
        print(f"Output saved to: {args.output_csv}")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input_csv}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
