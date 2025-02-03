# OBS Input Logger
A Mouse & Keyboard Event Collection Tool for AI Behavior Cloning

## Setup

1. Download OBS from [official website](https://obsproject.com/).
2. Install [input overlay](https://github.com/univrsal/input-overlay) OBS plugin. Follow [this tutorial](https://www.youtube.com/watch?v=7DTVIh3w6U8) by the author.

## Logging input events

The plugin provides a websocket server that streams mouse & keyboard events.

Once installation is complete, go to `Tools` -> `input-overlay settings` -> `WebSocket server`. The default websocket address is `0.0.0.0/16899` and this address is where our python script / client will listen to.

We'll be using websocket-client 

```
pip install websocket-client
```

it's fairly simple to use. Check out [`s1_simple_websocket_example.py`](s1_simple_websocket_example.py) for a simple example; run it while OBS is on (don't need to be recording / streaming), move your mouse or click something, you'll see M&K events gets printed.

now we just need to store this data somewhere :)

## Hooking client script to OBS

OBS provides a very useful scripts feature set incuding a [frontend API](https://docs.obsproject.com/reference-frontend-api). Checkout [`s2_simple_obs_trigger_example.py`](s2_simple_obs_trigger_example.py) for a simple example.

To add the client python script in OBS, go to `Tools -> Scripts` and add [`s3_obs_recording_client.py`](s3_obs_recording_client.py) into the loaded scripts. Afterwards, go to `Python Settings` tab and select path to the python you use.Note that you'll need to run `pip install websocket-client` on the same python you selected.

That's it. Restart OBS and it'll be ready for all recording moving forward. 

You'll find your recording mp4 and action csv both in the same save recording directory you configured in OBS. 

## Down sampling action data

The raw action data has very frequent events down to every other millisecond. We need to down sample this data to a more manageable frequency.

I chosed 60 FPS, meaning roughly 16-17ms per action / row in the recorded csv. I envision this to be a time for 1 observation, 1 inference and 1 action.

Run the following to down sample the data:

```
python s4_data_post_processing.py <recorded_actions.csv> <down_sampled_actions.csv>
```

## Replaying action data

run `python s5_replaying_recorded_events.py <down_sampled_actions.csv>` to replay the action data.

Note you might need to setup your desktop environment to match the beginning state of your recording.