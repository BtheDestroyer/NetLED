import rpi_ws281x
import log, net

import cfg
config = cfg.config["led"]
initialized = False
strip = None

def is_initialized():
    return initialized

def set_pixel(index : int, color : int, show : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if index < 0:
        index += config["count"] 
    if index >= config["count"] or index < 0:
        log.error("Tried to set color of pixel %d hen the strip is only %d pixels long" % (index, config["count"]))
    log.verbose("Setting pixel %d to (%d, %d, %d)" % (index, color % 0xFF, (color >> 8) % 0xFF, (color >> 16) % 0xFF))
    strip.setPixelColor(index, color)
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

class Set_Pixel_Packet(net.Packet):
    def __init__(self, pixel : int = 0, color : int = 0, show : bool = True):
        self.pixel = pixel
        self.color = color
        self.show = show

    @staticmethod
    def from_bytes(buffer : bytes):
        packet = Set_Pixel_Packet()
        packet.pixel = int.from_bytes(buffer[0:4], 'little')
        log.info("Decoded packet.pixel: %s => %d" % (buffer[0:4], packet.pixel))
        packet.color = int.from_bytes(buffer[4:8], 'little')
        log.info("Decoded packet.color: %s => %d" % (buffer[4:8], packet.color))
        packet.show = bool.from_bytes(buffer[8:9], 'little')
        log.info("Decoded packet.show: %s => %s" % (buffer[8:9], packet.show))
        return packet, buffer[9:]

    def to_bytes(self):
        packet_id = net.PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Set_Pixel_Packet")
            return
        log.info("Encoding packet_id: %d" % (packet_id))
        buffer = packet_id.to_bytes(4, 'little')
        log.info("to_bytes result buffer: %s" % (buffer))
        log.info("Encoding self.pixel: %d" % (self.pixel))
        buffer += self.pixel.to_bytes(4, 'little')
        log.info("to_bytes result buffer: %s" % (buffer))
        log.info("Encoding self.color: %x" % (self.color))
        buffer += self.color.to_bytes(4, 'little')
        log.info("to_bytes result buffer: %s" % (buffer))
        log.info("Encoding self.show: %s" % (self.show))
        buffer += self.show.to_bytes(1, 'little')
        log.info("to_bytes result buffer: %s" % (buffer))
        return buffer

    def execute(self):
        set_pixel(self.pixel, self.color)
net.PacketManager.register(Set_Pixel_Packet)

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
