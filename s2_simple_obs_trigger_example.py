import obspython as obs

def script_description():
    return "Hello World - Prints when recording starts/stops"

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)
    print("Hello! Script loaded successfully!")

def script_unload():
    print("Goodbye! Script unloaded!")

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTING:
        print("🎥 Recording is starting...")
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        print("🎥 Recording has started!")
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPING:
        print("🛑 Recording is stopping...")
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        print("🛑 Recording has stopped!")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTING:
        print("📡 Streaming is starting...")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        print("📡 Streaming has started!")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPING:
        print("🔴 Streaming is stopping...")
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        print("🔴 Streaming has stopped!")