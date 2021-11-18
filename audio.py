import pyaudio

import cfg
config = cfg.config["audio"]
p = pyaudio.PyAudio()

def speaker_stream():
    return p.open(format=pyaudio.paInt16,
                  channels=config["channels"],
                  rate=config["rate"],
                  input=True,
                  frames_per_buffer=config["chunk"])
