#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import _thread, threading, socket

connection_lock = threading.Lock()
connections = []
running = True

def handle_packet():
    pass

def handle_connection(connection, addr):
    connection_lock.acquire()
    connections.append(connection)
    connection_id = len(connections) - 1
    connection_lock.release()
    connection.settimeout(10)
    log.info("[%d] Awaiting packet..." % (connection_id))
    try:
        while True:
            packet = connection.recv(net.packet_size)
            if len(packet) > 0:
                log.info("[%d] Handling packet: %s" % (connection_id, packet))
                net.PacketManager.handle_buffer(packet)
                log.info("[%d] Awaiting packet..." % (connection_id))
    except socket.timeout:
        pass
    log.info("Connection closed with %s" % (addr[0]))
    connection_lock.acquire()
    connections[connection_id] = None
    connection_lock.release()

def main():
    log.info("Starting server for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.default_port)
    args = parser.parse_args()
    s = net.host_socket(args.port)
    if s is None:
        log.error("[MASTER] Failed to host!")
        return
    while running:
        c, addr = s.accept()
        log.info("[MASTER] New connection from %s" % (addr[0]))
        _thread.start_new_thread(handle_connection, (c, addr))
    log.info("[MASTER] Closing server...")
    s.close()
    log.info("Done!")

if __name__ == "__main__":
    main()
