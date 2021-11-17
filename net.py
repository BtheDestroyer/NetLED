import log, project
import socket

import cfg
config = cfg.config["net"]
packet_size = config["packet_size"]
default_port = config["default_port"]

def host_socket(port : int = default_port):
    s = socket.socket()
    try:
        s.bind(('', port))
    except:
        log.error("Failed to bind port %d" % (port))
        return
    s.listen()
    return s

def connect_socket(address : str, port : int = default_port):
    s = socket.socket()
    try:
        s.connect((address, port))
    except:
        log.error("Failed to connect to %s:%d" % (address, port))
        return
    return s

class Packet:
    def __init__(self):
        pass

    @staticmethod
    def from_bin(buffer : bytes):
        raise NotImplementedError()

    def to_bin(self):
        raise NotImplementedError()

class PacketManager:
    packet_types = []

    @staticmethod
    def register(packet):
        PacketManager.packet_types.append(packet)
        return PacketManager.packet_types.count - 1

    @staticmethod
    def get_packet_id(packet):
        for i in range(len(PacketManager.packet_types)):
            if type(packet) == type(PacketManager.packet_types[i]):
                return i
        return None

    @staticmethod
    def handle_buffer(buffer : bytes):
        if buffer.count == 0:
            log.error("Buffer given to PacketManager is empty")
            return
        if PacketManager.packet_types.count < buffer[0]:
            log.error("Buffer given to PacketManager is for a type of packet that is not managed")
            return
        return PacketManager.packet_types[buffer[0]].from_bin(buffer[1:])

