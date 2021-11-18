import threading

import cfg
config = cfg.config["log"]
logpath = config["path"]
file = None

log_lock = threading.Lock()

def is_open():
    return file is not None

def open_file(path : str = logpath):
    if is_open():
        file.close()
    logpath = path
    file = open(path, "w")

def tee(message : str):
    log_lock.acquire()
    if not message.endswith("\n"):
        message += "\n"
    if not is_open():
        open_file()
    if is_open():
        file.write(message)
    print(message, end="")
    log_lock.release()

def verbose(message : str):
    if config["levels"]["verbose"]:
        tee("[VER] " + message)

def info(message : str):
    if config["levels"]["info"]:
        tee("[INF] " + message)

def warning(message : str):
    if config["levels"]["warning"]:
        tee("[WAR] " + message)

def error(message : str):
    if config["levels"]["error"]:
        tee("[ERR] " + message)

def critical(message : str):
    if config["levels"]["critical"]:
        tee("[CRI] " + message)
