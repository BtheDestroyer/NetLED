import cfg
config = cfg.config["log"]
logpath = config["path"]
file = None

def is_open():
    return file is not None

def open(path : str = logpath):
    if is_open():
        file.close()
    logpath = path
    file = open(path, "w")

def tee(message : str):
    if not message.endswith("\n"):
        message += "\n"
    if is_open():
        file.write(message)
    print(message)

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
