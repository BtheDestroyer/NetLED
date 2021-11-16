import rpi_ws281x
import log

import cfg
config = cfg.config["led"]
initialized = False
strip = None

def is_initialized():
    return initialized

def set_pixel(index : int, color : rpi_ws281x.Color, show : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if index < 0:
        index += config["count"] 
    if index >= config["count"] or index < 0:
        log.error("Tried to set color of pixel %d hen the strip is only %d pixels long" % (index, config["count"]))
    strip.setPixelColor(i, color)
    if show:
        strip.show()

def set_pixels(start : int, count : int, color : rpi_ws281x.Color, show : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if start < 0:
        start += config["count"] 
    if start >= config["count"] or start < 0:
        log.error("Tried to set color of pixels (%d,%d] when the strip is only %d pixels long" % (i, i + count, config["count"]))
    if count >= 0:
        for i in range(start, start + count):
            strip.setPixelColor(i, color)
    else:
        for i in range(start + count, start):
            strip.setPixelColor(i, color)
    if show:
        strip.show()

def update():
    if not is_initialized():
        log.error("Tried to update when strip is not initialized")
        return
    strip.show()

# Initialization
log.info("Initializing LED strip")
if is_initialized():
    log.warning("Strip already initialized. Reinitializing")
strip = rpi_ws281x.PixelStrip(
    config["count"],
    config["pin"],
    config["freq"],
    config["dma"],
    config["invert"],
    config["brightness"],
    config["channel"])
if strip is None:
    log.error("Failed to construct LED strip!")
else:
    strip.begin()
    initialized = True
    log.info("Initialized LEDs!")
