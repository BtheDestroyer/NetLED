import log, net

import cfg
config = cfg.config["led"]
initialized = False
strip = None
awaiting_show = False

def color(red, green, blue, white=0):
    return ((white & 0xFF) << 24) | ((red & 0xFF) << 16) | ((green & 0xFF) << 8) | (blue & 0xFF)

def is_initialized():
    global initialized
    return initialized

def set_pixel(index : int, color : int, show_now : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if index < 0:
        index += config["count"] 
    if index >= config["count"] or index < 0:
        log.error("Tried to set color of pixel %d hen the strip is only %d pixels long" % (index, config["count"]))
    log.verbose("Setting pixel %d to (%d, %d, %d)" % (index, (color >> 16) & 0xFF, (color >> 8) & 0xFF, (color >> 0) & 0xFF))
    global strip
    strip.setPixelColor(index, color)
    if show_now:
        show()

def set_pixels(start : int, count : int, color : int, show_now : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if start < 0:
        start += config["count"] 
    if start >= config["count"] or start < 0:
        log.error("Tried to set color of pixels (%d,%d] when the strip is only %d pixels long" % (start, start + count, config["count"]))
    global strip
    if count >= 0:
        for i in range(start, start + count):
            strip.setPixelColor(i, color)
    else:
        for i in range(start + count, start):
            strip.setPixelColor(i, color)
    if show_now:
        show()

def shift_pixels(start : int, count : int, shift : int, show_now : bool = False):
    if not is_initialized():
        log.error("Tried to set color of pixel when strip is not initialized")
        return
    if start < 0:
        start += config["count"] 
    global strip
    end = 0
    if count >= 0:
        end = start + count
    else:
        end = start
        start = start + count
    if shift > 0:
        for i in range(end - 1, start - 1, -1):
            new_color = strip.getPixelColor(i - shift)
            if i - shift < 0:
                new_color = 0
            strip.setPixelColor(i, new_color)
    elif shift < 0:
        for i in range(start, end):
            new_color = strip.getPixelColor(i - shift)
            if i - shift > config["count"]:
                new_color = 0
            strip.setPixelColor(i, new_color)
    if show_now:
        show()

def show():
    if not is_initialized():
        log.error("Tried to show when strip is not initialized")
        return
    global awaiting_show
    awaiting_show = True

def main_thread_update():
    global awaiting_show
    if awaiting_show:
        global strip
        strip.show()

@net.PacketManager.register
class Set_Pixel_Packet(net.Packet):
    def __init__(self, pixel : int = 0, color : int = 0, show : bool = True):
        self.pixel = pixel
        self.color = color
        self.show = show

    @staticmethod
    def from_bytes(buffer : bytes):
        packet = Set_Pixel_Packet()
        packet.pixel = int.from_bytes(buffer[0:4], 'little')
        log.verbose("Decoded packet.pixel: %s => %d" % (buffer[0:4], packet.pixel))
        packet.color = int.from_bytes(buffer[4:8], 'little')
        log.verbose("Decoded packet.color: %s => %x" % (buffer[4:8], packet.color))
        packet.show = bool.from_bytes(buffer[8:9], 'little')
        log.verbose("Decoded packet.show: %s => %s" % (buffer[8:9], packet.show))
        return packet, buffer[9:]

    def to_bytes(self):
        packet_id = net.PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Set_Pixel_Packet")
            return
        buffer = packet_id.to_bytes(4, 'little')
        buffer += self.pixel.to_bytes(4, 'little', signed=True)
        buffer += self.color.to_bytes(4, 'little')
        buffer += self.show.to_bytes(1, 'little')
        return buffer

    def execute(self):
        set_pixel(self.pixel, self.color, self.show)

@net.PacketManager.register
class Set_Pixels_Packet(net.Packet):
    def __init__(self, start : int = 0, count : int = 1, color : int = 0, show : bool = True):
        self.start = start
        self.count = count
        self.color = color
        self.show = show

    @staticmethod
    def from_bytes(buffer : bytes):
        packet = Set_Pixels_Packet()
        packet.start = int.from_bytes(buffer[0:4], 'little', signed=True)
        log.verbose("Decoded packet.start: %s => %d" % (buffer[0:4], packet.start))
        packet.count = int.from_bytes(buffer[4:8], 'little', signed=True)
        log.verbose("Decoded packet.count: %s => %d" % (buffer[0:4], packet.count))
        packet.color = int.from_bytes(buffer[8:12], 'little')
        log.verbose("Decoded packet.color: %s => %x" % (buffer[4:8], packet.color))
        packet.show = bool.from_bytes(buffer[12:13], 'little')
        log.verbose("Decoded packet.show: %s => %s" % (buffer[8:9], packet.show))
        return packet, buffer[13:]

    def to_bytes(self):
        packet_id = net.PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Set_Pixel_Packet")
            return
        buffer = packet_id.to_bytes(4, 'little')
        buffer += self.start.to_bytes(4, 'little', signed=True)
        buffer += self.count.to_bytes(4, 'little', signed=True)
        buffer += self.color.to_bytes(4, 'little')
        buffer += self.show.to_bytes(1, 'little')
        return buffer

    def execute(self):
        set_pixels(self.start, self.count, self.color, self.show)

@net.PacketManager.register
class Shift_Pixels_Packet(net.Packet):
    def __init__(self, start : int = 0, count : int = 1, shift : int = 1, show : bool = True):
        self.start = start
        self.count = count
        self.shift = shift
        self.show = show

    @staticmethod
    def from_bytes(buffer : bytes):
        packet = Shift_Pixels_Packet()
        packet.start = int.from_bytes(buffer[0:4], 'little', signed=True)
        log.verbose("Decoded packet.start: %s => %d" % (buffer[0:4], packet.start))
        packet.count = int.from_bytes(buffer[4:8], 'little', signed=True)
        log.verbose("Decoded packet.count: %s => %d" % (buffer[4:8], packet.count))
        packet.shift = int.from_bytes(buffer[8:12], 'little', signed=True)
        log.verbose("Decoded packet.shift: %s => %x" % (buffer[8:12], packet.shift))
        packet.show = bool.from_bytes(buffer[12:13], 'little')
        log.verbose("Decoded packet.show: %s => %s" % (buffer[12:13], packet.show))
        return packet, buffer[13:]

    def to_bytes(self):
        packet_id = net.PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Set_Pixel_Packet")
            return
        buffer = packet_id.to_bytes(4, 'little')
        buffer += self.start.to_bytes(4, 'little', signed=True)
        buffer += self.count.to_bytes(4, 'little', signed=True)
        buffer += self.shift.to_bytes(4, 'little', signed=True)
        buffer += self.show.to_bytes(1, 'little')
        return buffer

    def execute(self):
        shift_pixels(self.start, self.count, self.shift, self.show)

def initialize():
    log.info("Initializing LED strip")
    if is_initialized():
        log.warning("Strip already initialized. Reinitializing")
    try:
        rpi_ws281x = __import__("rpi_ws281x")
        global strip
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
            global initialized
            initialized = True
            log.info("Initialized LEDs!")
    except ImportError:
        log.critical("Can't import the module `rpi_ws281x`. Make sure this is running on a Raspberry Pi with it installed")
        raise
