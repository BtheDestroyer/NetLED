import yaml

config = {}
with open("config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Missing config.yaml")
        print(exc)
        exit(-1)
