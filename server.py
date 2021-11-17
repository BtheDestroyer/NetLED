#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import _thread, threading, socket

connections_lock = threading.Lock()
connections = []
running = True

def handle_packet():
    pass

def handle_connection(connection):
    connections_lock.acquire()
    connections.append(connection)
    connections_lock.release()
    try:
        while True:
            packet = connection.recv(net.packet_size)
            net.PacketManager.handle_buffer(packet)
    except socket.timeout:
        connections_lock.acquire()
        connections.remove(connection)
        connections_lock.release()

def main():
    log.info("Starting server for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.default_port)
    args = parser.parse_args()
    s = net.host_socket(args.port)
    if s is None:
        log.error("Failed to host!")
        return
    while running:
        c, addr = s.accept()
        log.info("New connection from %s" % (addr))
        _thread.start_new_thread(handle_connection, (c,))
    log.info("Closing server...")
    s.close()
    log.info("Done!")

if __name__ == "__main__":
    main()