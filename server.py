#!/usr/bin/python3
import log, project, net, argparse

def main():
    log.info("Starting server for " + project.name + " v" + project.version)

    log.info("Closing server")

if __name__ == "__main__":
    main()
