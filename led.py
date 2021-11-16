from rpi_ws281x import *
import log

import cfg
config = cfg.config["led"]
strip = None

def init():
    strip = Adafruit_NeoPixel(
        config["count"],
        config["pin"],
        config["freq"],
        config["dma"],
        config["invert"],
        config["brightness"],
        config["channel"])
    strip.begin()

def set_pixel(index : int, color : Color, show : bool = False):
    if index >= strip.numPixels():
        log.error("Tried to set color of pixel %d when the strip is only %d pixels long" % (index, strip.numPixels()))
    strip.setPixelColor(index, color)
    if show:
        strip.show()

def update():
    strip.show()
