from rpi_ws281x import *
import log

import cfg
config = cfg.config["led"]
strip = None

def init():
    log.info("Initializing LED strip")
    if strip is None:
        log.warning("Strip already initialized. Reinitializing")
    strip = Adafruit_NeoPixel(
        config["count"],
        config["pin"],
        config["freq"],
        config["dma"],
        config["invert"],
        config["brightness"],
        config["channel"])
    strip.begin()

def is_initialized():
    return strip is not None

def set_pixel(index : int, color : Color, show : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        log.error("Call `led.init()` first!")
        return
    if index >= config["count"]:
        log.error("Tried to set color of pixel %d when the strip is only %d pixels long" % (index, config["count"]))
    strip.setPixelColor(index, color)
    if show:
        strip.show()

def update():
    strip.show()
