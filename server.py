#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import _thread, threading, socket
import signal, sys

connection_lock = threading.Lock()
connections = []
running = True

def handle_connection(connection, addr):
    connection_lock.acquire()
    connections.append(connection)
    connection_id = len(connections) - 1
    connection_lock.release()
    connection.settimeout(10)
    connection_alive = True
    try:
        while connection_alive:
            log.info("[%d] Awaiting packet..." % (connection_id))
            buffer = connection.recv(net.buffer_size)
            if len(buffer) > 0:
                while len(buffer) > 0:
                    log.info("[%d] Handling buffer: %s" % (connection_id, buffer))
                    packet, remainingbuffer = net.PacketManager.parse_buffer(buffer)
                    log.info("[%d] Bytes used: %d" % (len(buffer) - len(remainingbuffer)))
                    packet.execute()
                    buffer = remainingbuffer
            else:
                connection_alive = False
    except socket.timeout:
        pass
    connection.close()
    log.info("[%d] Connection closed with %s" % (connection_id, addr[0]))
    connection_lock.acquire()
    connections[connection_id] = None
    connection_lock.release()

def main():
    signal.signal(signal.SIGINT, sigint)
    log.info("Starting server for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.default_port)
    args = parser.parse_args()
    s = net.host_socket(args.port)
    s.settimeout(1)
    if s is None:
        log.error("[MASTER] Failed to host!")
        return
    while running:
        log.verbose("[MASTER] Awaiting connection...")
        try:
            c, addr = s.accept()
            if c is not None:
                log.info("[MASTER] New connection from %s" % (addr[0]))
                _thread.start_new_thread(handle_connection, (c, addr))
        except socket.timeout:
            pass
    log.info("[MASTER] Closing server...")
    s.close()
    log.info("Done!")

def sigint(sig, frame):
    global running
    running = False
    log.info("Telling server to shut down...")

if __name__ == "__main__":
    main()
