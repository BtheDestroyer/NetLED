#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import time

def main():
    log.info("Starting client for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("address", type=str, help="Address to connect to", default="localhost")
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to connect with", default=net.default_port)
    args = parser.parse_args()
    log.info("Connecting to %s:%d" % (args.address, args.port))
    s = net.connect_socket(args.address, args.port)
    if s is None:
        log.error("Failed to connect socket!")
        return
    log.info("Sending pixel packet 0...")
    packet = led.Set_Pixel_Packet(0, rpi_ws281x.Color(255,0,0)).to_bytes()
    log.info("Packet: %s" % (packet))
    s.send(packet)
    log.info("Sleeping for 1 second...")
    time.sleep(1)
    log.info("Sending pixel packet 2...")
    packet = led.Set_Pixel_Packet(1, rpi_ws281x.Color(255,0,0)).to_bytes()
    log.info("Packet: %s" % (packet))
    s.send(packet)
    log.info("Sleeping for 1 second...")
    time.sleep(1)
    log.info("Sending pixel packet 3+4...")
    packet = led.Set_Pixel_Packet(0, rpi_ws281x.Color(0,0,0)).to_bytes()
    log.info("Packet: %s" % (packet))
    s.send(packet)
    packet = led.Set_Pixel_Packet(1, rpi_ws281x.Color(0,0,0)).to_bytes()
    log.info("Packet: %s" % (packet))
    s.send(packet)
    log.info("Closing socket...")
    s.close()
    log.info("Done!")

if __name__ == "__main__":
    main()
