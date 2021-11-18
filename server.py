#!/usr/bin/python3
import log, project, net, led
import argparse
import socket
import signal
import time

packets = []
running = True
connections = []
next_id = 0

def handle_connection(connection_id, connection, addr, last_message_time):
    try:
        log.verbose("[%6d] Awaiting packet..." % (connection_id))
        buffer = connection.recv(net.config["buffer_size"])
        if len(buffer) > 0:
            log.info("[%6d] Handling buffer (%d bytes)" % (connection_id, len(buffer)))
            global packets
            while len(buffer) > 0:
                packet, remainingbuffer = net.PacketManager.parse_buffer(buffer)
                packets.append(packet)
                buffer = remainingbuffer
            connection.send(net.Heartbeat_Packet().to_bytes())
            return True, time.time()
        else:
            return False, last_message_time
    except socket.timeout:
        return True, last_message_time

def master_server(s : socket.socket):
    if s is None:
        log.error("[MASTER] Failed to host!")
        return
    log.verbose("[MASTER] Awaiting connection...")
    try:
        c, addr = s.accept()
        if c is not None:
            log.info("[MASTER] New connection from %s" % (addr[0]))
            c.settimeout(0.01)
            global next_id
            connections.append([next_id, c, addr, time.time()])
            next_id += 1
    except socket.timeout:
        pass

def server():
    pass

def main():
    signal.signal(signal.SIGINT, sigint)
    log.info("Starting server for " + project.name + " v" + project.version)
    led.initialize()
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to host with", default=net.config["default_port"])
    args = parser.parse_args()
    master_socket = net.host_socket(args.port)
    if master_socket is None:
        log.critical("Failed to host server!")
        return
    master_socket.settimeout(0.01)
    global packets
    while running:
        master_server(master_socket)
        for c in connections:
            give_focus = True
            keep_alive = True
            while give_focus:
                keep_alive, last_message_time = handle_connection(*c)
                c[3] = last_message_time
                timeout = time.time() - last_message_time < net.config["connection_timeout"]
                keep_alive &= timeout
                give_focus = keep_alive and timeout < 0.01
                if len(packets) > 0:
                    for packet in packets:
                        packet.execute()
                    packets.clear()
                    led.main_thread_update()
            if not keep_alive:
                reason = "Unknown reason"
                if timeout:
                    reason = "Connection timed out; too long since last message"
                elif not keep_alive:
                    reason = "Connection closed by the client"
                log.info("[MASTER] Connection %d closed (%s)" % (c[0], reason))
                connections.remove(c)
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
