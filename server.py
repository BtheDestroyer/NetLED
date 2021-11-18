#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import _thread, threading, socket

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
                log.info("[%d] Handling buffer: %s" % (connection_id, buffer))
                packet, buffer = net.PacketManager.parse_buffer(buffer)
                packet.execute()
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
    log.info("Set_Pixel_Packet.packet_id = %d" % (led.Set_Pixel_Packet.packet_id))
    log.info("len(net.packet_types) = %d" % (len(net.packet_types)))
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
