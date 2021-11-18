#!/usr/bin/python3
import log, project, net, led, audio
import argparse
import time
import socket
import inspect
import keyboard
import numpy

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

def setpixel(s : socket.socket, index : str, r : str, g : str, b : str):
    index = int(index)
    r = int(r)
    g = int(g)
    b = int(b)
    log.info("Setting pixel %d to (%d, %d, %d)..." % (index, r, g, b))
    packet = led.Set_Pixel_Packet(index, led.color(r,g,b)).to_bytes()
    s.send(packet)

def setpixels(s : socket.socket, start : str, count: str, r : str, g : str, b : str):
    start= int(start)
    count = int(count)
    r = int(r)
    g = int(g)
    b = int(b)
    log.info("Setting pixels (%d, %d] to (%d, %d, %d)..." % (start, start + count, r, g, b))
    packet = led.Set_Pixels_Packet(start, count, led.color(r,g,b)).to_bytes()
    s.send(packet)

def shiftpixels(s : socket.socket, start : str, count: str, shift :str):
    start= int(start)
    count = int(count)
    shift = int(shift)
    log.info("Shifting pixels (%d, %d] by %d..." % (start, start + count, shift))
    packet = led.Shift_Pixels_Packet(start, count, shift).to_bytes()
    s.send(packet)

def streamaudio(s : socket.socket, device_id : str, r : str, g : str, b : str):
    device_id = int(device_id)
    r = int(r)
    g = int(g)
    b = int(b)
    stream = audio.open_stream(device_id)
    buffer = bytes()
    try:
        while True:
            frame = numpy.frombuffer(stream.read(audio.config["chunk"]), dtype=numpy.float32)
            volume = 0
            for sample in frame:
                volume = max(volume, abs(sample))
            buffer += led.Shift_Pixels_Packet(0, led.config["count"], 1, True).to_bytes()
            buffer += led.Set_Pixel_Packet(0, led.color(r * volume, g * volume, b * volume), False).to_bytes()
            if len(buffer) > net.config["buffer_size"] / 4:
                log.info("Volume: %f" % (volume,))
                s.send(buffer)
                # Wait for server to tell us to keep going
                buffer = bytes()
                #while len(buffer) == 0:
                #    buffer = s.recv(net.config["buffer_size"])
    except KeyboardInterrupt:
        pass

def listaudiodevices(s : socket.socket):
    for device in audio.list_all_devices():
        log.info("Index: %d, Name: %s" % (device["index"], device["name"]))

def pulse(s : socket.socket, r : str, g : str, b : str, wait_ms : str, length : str):
    r = int(r)
    g = int(g)
    b = int(b)
    wait_ms = float(wait_ms)
    length = int(length)
    log.info("Pulsing...")
    buffer = bytes()
    for i in range(led.config["count"] + length):
        buffer += led.Shift_Pixels_Packet(0, led.config["count"], 1, True).to_bytes()
        if i < length:
            buffer += led.Set_Pixel_Packet(0, led.color(r, g, b), False).to_bytes()
        buffer += net.Sleep_Packet(wait_ms / 1000.0).to_bytes()
        if len(buffer) > net.config["buffer_size"] / 4:
            s.send(buffer)
            # Wait for server to tell us to keep going
            buffer = bytes()
            while len(buffer) == 0:
                buffer = s.recv(net.config["buffer_size"])
    if len(buffer) > 0:
        s.send(buffer)

subcommands = {
    "demo": demo,
    "setpixel": setpixel,
    "setpixels": setpixels,
    "shiftpixels": shiftpixels,
    "streamaudio": streamaudio,
    "listaudiodevices": listaudiodevices,
    "pulse": pulse,
}

def main():
    log.info("Starting client for " + project.name + " v" + project.version)
    parser = argparse.ArgumentParser()
    parser.add_argument("subcommand", type=str, help="Command to send to the server", nargs='?', default="demo", const="demo")
    parser.add_argument("subarguments", type=str, help="Arguments for the subcommand", nargs='*')
    parser.add_argument("-a", metavar="address", dest="address", type=str, help="Address to connect to", default="localhost", const="localhost", nargs='?')
    parser.add_argument("-p", metavar="port", dest="port", type=int, help="Port to connect with", default=net.config["default_port"])
    args = parser.parse_args()
    if args.subcommand is not None:
        if args.subcommand in subcommands.keys():
            subcommand = subcommands[args.subcommand]
            signature = inspect.signature(subcommand)
            param_count = len(signature.parameters) - 1
            if param_count == len(args.subarguments):
                log.info("Connecting to %s:%d" % (args.address, args.port))
                s = net.connect_socket(args.address, args.port)
                if s is None:
                    log.error("Failed to connect socket!")
                    return
                s.settimeout(10)
                try:
                    subcommand(s, *args.subarguments)
                    # Wait for server to tell us it's done
                    buffer = bytes()
                    while len(buffer) == 0:
                        buffer = s.recv(net.config["buffer_size"])
                    s.close()
                except socket.timeout:
                    log.error("Connection timed out!")
            else:
                params = list(signature.parameters.keys())[1:]
                log.error("The subcommand \"%s\" requires %d arguments: %s" % (args.subcommand, param_count, params))
        else:
            log.error("There is no subcommand named \"%s\"" % (args.subcommand))
        return

if __name__ == "__main__":
    main()
