#!/usr/bin/python3
import log, project, net, led, audio
import argparse
import time
import socket
import inspect

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

def shiftpixels(s : socket.socket, start : str, count: str, shift :str):
    start= int(start)
    count = int(count)
    shift = int(shift)
    log.info("Shifting pixels (%d, %d] by %d..." % (start, start + count, shift))
    packet = led.Shift_Pixels_Packet(start, count, shift).to_bytes()
    s.send(packet)
    time.sleep(1)
    s.close()

def streamaudio(s : socket.socket):
    speakers = audio.speaker_stream()

def pulse(s : socket.socket, r : str, g : str, b : str, wait_ms : str, length : str):
    r = int(r)
    g = int(g)
    b = int(b)
    wait_ms = float(wait_ms)
    length = int(length)
    log.info("Pulsing...")
    buffer = bytes()
    for i in range(led.config["count"] + length):
        buffer += led.Shift_Pixels_Packet(0, led.config["count"], 1).to_bytes()
        if i < length:
            buffer += led.Set_Pixel_Packet(0, led.color(r, g, b)).to_bytes()
        if len(buffer) >= net.config["buffer_size"] / 4:
            s.send(buffer)
            buffer = bytes()
        buffer += net.Sleep_Packet(wait_ms / 1000.0).to_bytes()
        time.sleep(wait_ms / 1000.0)
    if len(buffer) >= 0:
        s.send(buffer)
    time.sleep(1)
    s.close()


subcommands = {
    "demo": demo,
    "setpixel": setpixel,
    "setpixels": setpixels,
    "shiftpixels": shiftpixels,
    "streamaudio": streamaudio,
    "pulse": pulse,
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
                params = list(signature.parameters.keys())[1:]
                log.error("The subcommand \"%s\" requires %d arguments: %s" % (args.subcommand, param_count, params))
        else:
            log.error("There is no subcommand named \"%s\"" % (args.subcommand))
        return
    

if __name__ == "__main__":
    main()
