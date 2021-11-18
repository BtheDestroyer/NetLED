#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import threading, socket
import signal, sys

packet_lock = threading.Lock()
packets = []
running = True

def handle_connection(connection, addr, connection_id):
    connection.settimeout(10)
    connection_alive = True
    try:
        while connection_alive:
            log.info("[%d] Awaiting packet..." % (connection_id))
            buffer = connection.recv(net.buffer_size)
            if len(buffer) > 0:
                packet_lock.acquire()
                global packets
                while len(buffer) > 0:
                    log.info("[%d] Handling buffer: %s" % (connection_id, buffer))
                    packet, remainingbuffer = net.PacketManager.parse_buffer(buffer)
                    log.info("[%d] Bytes used: %d / %d" % (connection_id, len(buffer) - len(remainingbuffer), len(buffer)))
                    packets.append(packet)
                    buffer = remainingbuffer
                packet_lock.release()
            else:
                connection_alive = False
    except socket.timeout:
        pass
    connection.close()
    log.info("[%d] Connection closed with %s" % (connection_id, addr[0]))

def master_server(s : socket.socket):
    s.settimeout(1)
    if s is None:
        log.error("[MASTER] Failed to host!")
        return
    connections = []
    next_id = 0
    while running:
        log.verbose("[MASTER] Awaiting connection...")
        try:
            c, addr = s.accept()
            if c is not None:
                log.info("[MASTER] New connection from %s" % (addr[0]))
                c_thread = threading.Thread(target=handle_connection, args=(c, addr, next_id))
                c_thread.start()
                connections.append((next_id, c_thread, addr))
                next_id += 1
        except socket.timeout:
            pass
    log.info("[MASTER] Closing server...")
    for connection in connections:
        log.info("[MASTER] Joining connection %d..." % (connection[0]))
        connection[1].join()
    s.close()

def main():
    signal.signal(signal.SIGINT, sigint)
    log.info("Starting server for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.default_port)
    args = parser.parse_args()
    master_thread =threading.Thread(target=master_server, args=(net.host_socket(args.port),))
    master_thread.start()
    global packets
    while running:
        if len(packets) > 0:
            packet_lock.acquire()
            packets_copy = packets.copy()
            packets.clear()
            packet_lock.release()
            for packet in packets_copy:
                packet.execute()
            led.main_thread_update()
    master_thread.join()
    log.info("Done!")

def sigint(sig, frame):
    global running
    running = False
    log.info("Telling server to shut down...")

if __name__ == "__main__":
    main()
