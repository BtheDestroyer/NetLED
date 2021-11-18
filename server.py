#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import socket
import signal, sys

packets = []
running = True
connections = []
next_id = 0

def handle_connection(connection_id, connection, addr):
    try:
        log.info("[%6d] Awaiting packet..." % (connection_id))
        buffer = connection.recv(net.buffer_size)
        if len(buffer) > 0:
            global packets
            while len(buffer) > 0:
                log.info("[%6d] Handling buffer: %s" % (connection_id, buffer))
                packet, remainingbuffer = net.PacketManager.parse_buffer(buffer)
                log.info("[%6d] Bytes used: %d / %d" % (connection_id, len(buffer) - len(remainingbuffer), len(buffer)))
                packets.append(packet)
                buffer = remainingbuffer
            return True
        else:
            return False
    except socket.timeout:
        return True

def master_server(s : socket.socket):
    if s is None:
        log.error("[MASTER] Failed to host!")
        return
    log.verbose("[MASTER] Awaiting connection...")
    try:
        c, addr = s.accept()
        if c is not None:
            log.info("[MASTER] New connection from %s" % (addr[0]))
            c.settimeout(1)
            global next_id
            connections.append((next_id, c, addr))
            next_id += 1
    except socket.timeout:
        pass

def main():
    signal.signal(signal.SIGINT, sigint)
    log.info("Starting server for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.default_port)
    args = parser.parse_args()
    master_socket = net.host_socket(args.port)
    master_socket.settimeout(1)
    global packets
    while running:
        master_server(master_socket)
        for c in connections:
            if not handle_connection(*c):
                connections.remove(c)
        if len(packets) > 0:
            for packet in packets:
                packet.execute()
            packets.clear()
            led.main_thread_update()
    log.info("[MASTER] Closing server...")
    for connection in connections:
        log.info("[MASTER] Joining connection %d..." % (connection[0]))
        connection[1].close()
    master_socket.close()
    log.info("Done!")

def sigint(sig, frame):
    global running
    running = False
    log.info("Telling server to shut down...")

if __name__ == "__main__":
    main()
