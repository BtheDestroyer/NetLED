#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import _thread, threading, socket

running = True

def handle_packet():
    pass

def handle_connection(connection, addr):
    connection.setblocking(True)
    try:
        while True:
            packet = connection.recv(net.packet_size)
            if len(packet) > 0:
                log.info("Handling packet: %s" % (packet))
                net.PacketManager.handle_buffer(packet)
    except socket.timeout:
        pass
    log.info("Connection closed with %s" % (addr[0]))

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
        log.info("New connection from %s" % (addr[0]))
        _thread.start_new_thread(handle_connection, (c, addr))
    log.info("Closing server...")
    s.close()
    log.info("Done!")

if __name__ == "__main__":
    main()
