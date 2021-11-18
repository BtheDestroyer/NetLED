import pyaudio

import cfg
config = cfg.config["audio"]
p = pyaudio.PyAudio()

def list_all_devices():
    devices = []
    for i in range(0, p.get_device_count()):
        info = p.get_device_info_by_index(i)
        devices.append(info)
    return devices

def open_stream(device_id):
    device = p.get_device_info_by_index(device_id)
    channel_count = device["maxInputChannels"] if (device["maxOutputChannels"] < device["maxInputChannels"]) else device["maxOutputChannels"]
    return p.open(format=pyaudio.paFloat32,
                  channels=channel_count,
                  rate=int(device["defaultSampleRate"]),
                  input=True,
                  frames_per_buffer=config["chunk"],
                  input_device_index=device["index"])
