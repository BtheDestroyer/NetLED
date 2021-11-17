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
    def from_bytes(buffer : bytes):
        raise NotImplementedError()

    def to_bytes(self):
        raise NotImplementedError()

class PacketManager:
    packet_types = []

    @staticmethod
    def register(packet : type):
        log.info("Registering packet type %s as id %d" % (packet.__name__, len(PacketManager.packet_types)))
        PacketManager.packet_types.append(packet)
        return len(PacketManager.packet_types) - 1

    @staticmethod
    def get_packet_id(packet):
        for i in range(len(PacketManager.packet_types)):
            if type(packet) == type(PacketManager.packet_types[i]):
                return i
        return None

    @staticmethod
    def handle_buffer(buffer : bytes):
        if len(buffer) == 0:
            log.error("Buffer given to PacketManager is empty")
            return
        packet_id = int.from_bytes(buffer)
        if len(PacketManager.packet_types) < packet_id:
            log.error("Buffer given to PacketManager is for a type of packet that is not managed")
            return
        return PacketManager.packet_types[packet_id].from_bytes(buffer[len(int.to_bytes(packet_id)):])

