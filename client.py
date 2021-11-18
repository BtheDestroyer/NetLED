#!/usr/bin/python3
import log, project, net, led
import argparse
import time
import socket
import inspect

def setpixel(s : socket.socket, index : str, r : str, g : str, b : str):
    index = int(index)
    r = int(r)
    g = int(g)
    b = int(b)
    log.info("Setting pixel %d to (%d, %d, %d)..." % (index, r, g, b))
    packet = led.Set_Pixel_Packet(index, led.color(r,g,b)).to_bytes()
    s.send(packet)
    time.sleep(1)
    s.close()

def setpixels(s : socket.socket, start : str, count: str, r : str, g : str, b : str):
    start= int(start)
    count = int(count)
    r = int(r)
    g = int(g)
    b = int(b)
    log.info("Setting pixels (%d, %d] to (%d, %d, %d)..." % (start, start + count, r, g, b))
    packet = led.Set_Pixels_Packet(start, count, led.color(r,g,b)).to_bytes()
    s.send(packet)
    time.sleep(1)
    s.close()

def demo(s : socket.socket):
    log.info("Sending pixel packet 0...")
    packet = led.Set_Pixel_Packet(0, led.color(255,0,255)).to_bytes()
    s.send(packet)
    log.info("Sleeping for 1 seconds...")
    time.sleep(1)
    log.info("Sending pixel packet 2...")
    packet = led.Set_Pixel_Packet(1, led.color(128,255,0)).to_bytes()
    s.send(packet)
    log.info("Sleeping for 1 seconds...")
    time.sleep(1)
    log.info("Sending pixel packet 3...")
    packet = led.Set_Pixel_Packet(2, led.color(0,128,255)).to_bytes()
    s.send(packet)
    log.info("Sleeping for 1 seconds...")
    time.sleep(1)
    log.info("Sending pixel packet 4,5,6...")
    packet  = led.Set_Pixel_Packet(0, led.color(0,0,0)).to_bytes()
    packet += led.Set_Pixel_Packet(1, led.color(0,0,0)).to_bytes()
    packet += led.Set_Pixel_Packet(2, led.color(0,0,0)).to_bytes()
    s.send(packet)
    time.sleep(1)
    log.info("Closing socket...")
    s.close()
    log.info("Done!")

subcommands = {
    "demo": demo,
    "setpixel": setpixel,
    "setpixels": setpixels,
}

def main():
    log.info("Starting client for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("subcommand", type=str, help="Command to send to the server", nargs='?', default="demo", const="demo")
    parser.add_argument("subarguments", type=str, help="Arguments for the subcommand", nargs='*')
    parser.add_argument("-a", metavar="address", dest="address", type=str, help="Address to connect to", default="localhost", const="localhost", nargs='?')
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
                params = signature.parameters.keys()[1:]
                log.error("The subcommand \"%s\" requires %d arguments: %s" % (args.subcommand, param_count, params))
        else:
            log.error("There is no subcommand named \"%s\"" % (args.subcommand))
        return
    

if __name__ == "__main__":
    main()
