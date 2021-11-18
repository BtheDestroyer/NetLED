import log, project
import socket

import cfg
config = cfg.config["net"]
buffer_size = config["buffer_size"]
default_port = config["default_port"]
packet_types = []

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
            log.error("Buffer given to PacketManager is for a type of packet that is not managed")
            return
        return packet_types[packet_id].from_bytes(buffer[4:])

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
PacketManager.register(Packet)

class Heartbeat_Packet(Packet):
    def __init__(self):
        pass

    @staticmethod
    def from_bytes(buffer : bytes):
        return buffer

    def to_bytes(self):
        return bytes()

    def execute(self):
        pass
PacketManager.register(Heartbeat_Packet)
