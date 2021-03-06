import log
import socket
import struct
import time

import cfg
config = cfg.config["net"]
packet_types = []

def host_socket(port : int = config["default_port"]):
    s = socket.socket()
    try:
        s.bind(('', port))
    except:
        log.error("Failed to bind port %d" % (port))
        return
    s.listen()
    return s

def connect_socket(address : str, port : int = config["default_port"]):
    s = socket.socket()
    try:
        s.connect((address, port))
    except:
        log.error("Failed to connect to %s:%d" % (address, port))
        return
    return s

class PacketManager:
    @staticmethod
    def register(packet : type):
        global packet_types
        log.info("Registering packet type %s as id %d" % (packet.__name__, len(packet_types)))
        packet_types.append(packet)
        return packet

    @staticmethod
    def get_packet_id(packet):
        global packet_types
        for i in range(len(packet_types)):
            if type(packet) == packet_types[i]:
                return i
        return None

    @staticmethod
    def parse_buffer(buffer : bytes):
        if len(buffer) == 0:
            log.error("Buffer given to PacketManager is empty")
            return
        packet_id = int.from_bytes(buffer[0:4], 'little')
        global packet_types
        if len(packet_types) < packet_id:
            log.error("Buffer given to PacketManager is for a type of packet that is not managed (%d)" % (packet_id,))
            return
        return packet_types[packet_id].from_bytes(buffer[4:])

@PacketManager.register
class Packet:
    def __init__(self):
        pass

    @staticmethod
    def from_bytes(buffer : bytes):
        raise NotImplementedError()

    def to_bytes(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

@PacketManager.register
class Heartbeat_Packet(Packet):
    def __init__(self):
        pass

    @staticmethod
    def from_bytes(buffer : bytes):
        return Heartbeat_Packet(), buffer

    def to_bytes(self):
        packet_id = PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Heartbeat_Packet")
            return
        buffer = packet_id.to_bytes(4, 'little')
        return buffer

    def execute(self):
        pass

@PacketManager.register
class Sleep_Packet(Packet):
    def __init__(self, time : float = 1):
        self.time = time

    @staticmethod
    def from_bytes(buffer : bytes):
        packet = Sleep_Packet()
        packet.time = struct.unpack("f", buffer[0:4])[0]
        return packet, buffer[4:]

    def to_bytes(self):
        packet_id = PacketManager.get_packet_id(self)
        if packet_id is None:
            log.error("Couldn't get packet id for Sleep_Packet")
            return
        buffer = packet_id.to_bytes(4, 'little')
        buffer += struct.pack("f", self.time)
        return buffer

    def execute(self):
        time.sleep(self.time)
