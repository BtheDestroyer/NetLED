#!/usr/bin/python3
import rpi_ws281x
import log, project, net, led
import argparse
import time
import socket
import inspect

def setpixel(s : socket.socket, index, r, g, b):
    index = int(index)
    r = int(r)
    g = int(g)
    b = int(b)
    log.info("Setting pixel %d to (%d, %d, %d)..." % (index, r, g, b))
    packet = led.Set_Pixel_Packet(index, rpi_ws281x.Color(r,g,b)).to_bytes()
    s.send(packet)

def demo(s : socket.socket):
    log.info("Sending pixel packet 0...")
    packet = led.Set_Pixel_Packet(0, rpi_ws281x.Color(255,0,0)).to_bytes()
    s.send(packet)
    log.info("Sleeping for 1 second...")
    time.sleep(1)
    log.info("Sending pixel packet 2...")
    packet = led.Set_Pixel_Packet(1, rpi_ws281x.Color(255,0,0)).to_bytes()
    s.send(packet)
    log.info("Sleeping for 1 second...")
    time.sleep(1)
    log.info("Sending pixel packet 3+4...")
    packet = led.Set_Pixel_Packet(0, rpi_ws281x.Color(0,0,0)).to_bytes()
    s.send(packet)
    packet = led.Set_Pixel_Packet(1, rpi_ws281x.Color(0,0,0)).to_bytes()
    s.send(packet)
    log.info("Closing socket...")
    s.close()
    log.info("Done!")

subcommands = {
    "demo": demo,
    "setpixel": setpixel
}

def main():
    log.info("Starting client for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("address", type=str, help="Address to connect to", const="localhost", nargs='?')
    parser.add_argument("subcommand", type=str, help="Command to send to the server", nargs='?', default="demo", const="demo")
    parser.add_argument("subarguments", type=str, help="Arguments for the subcommand", nargs='*')
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to connect with", default=net.default_port)
    args = parser.parse_args()
    log.info("Connecting to %s:%d" % (args.address, args.port))
    s = net.connect_socket(args.address, args.port)
    if s is None:
        log.error("Failed to connect socket!")
        return
    if args.subcommand is not None:
        if args.subcommand in subcommands.keys():
            subcommand = subcommands[args.subcommand]
            signature = inspect.signature(subcommand)
            param_count = len(signature.parameters) - 1
            if param_count == len(args.subarguments):
                subcommand(s, *args.subarguments)
            else:
                params = [key for key in signature.parameters.keys() if key != "s"]
                log.error("The subcommand \"%s\" requires %d arguments: %s" % (args.subcommand, param_count, params))
        else:
            log.error("There is no subcommand named \"%s\"" % (args.subcommand))
        return
    

if __name__ == "__main__":
    main()
