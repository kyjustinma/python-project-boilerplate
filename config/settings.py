"""
This file is used to store any global variables such as file paths etc
"""
import os
import time
import typing
import socket
import logging
import logging.config
import yaml

from dotenv import dotenv_values

env_config = dotenv_values(".env")
file_path = os.path.dirname(os.path.realpath(__file__))


global logger


def __init__():  # On initialisation
    print("")
    global config
    config = {}
    ### Getting ENV from dotenv
    env_get("VERBOSE", default=3, type=int)
    env_get("FLASK_PORT", 8080, type=int)
    env_get("FLASK_IP", get_ip())

    mappings()
    logger_init("lol")
    print("")


def env_get(variable_name: str, default: str, type: str = "string") -> str or float:
    try:
        if type != "string":
            config[variable_name] = type(env_config[variable_name])
        else:
            config[variable_name] = env_config[variable_name]
    except Exception as e:
        print(f"\t[.ENV] Missing [{variable_name}] setting to '{default}'")
        if type != "string":
            config[variable_name] = type(default)
        else:
            config[variable_name] = default


def get_ip():
    host_name = socket.gethostname()
    _IP = socket.gethostbyname(host_name).strip()
    return _IP.strip()


def mappings():
    mapping = {0: "Text0", 1: "Text1", 2: "Text2", 3: "Text3"}
    config["RELAY_MAPPING"] = mapping

    config["WHEEL_CMD"] = [
        "List",
        "Example",
        "For",
        "Template",
    ]


def logger_init(name):
    logging_yaml_path = os.path.join(file_path, "logger_setting.yaml")
    with open(logging_yaml_path, "r") as f:
        yaml_config = yaml.full_load(f)
        logging.config.dictConfig(yaml_config)
    logger = logging.getLogger(name=name)
    return logger


logger = logger_init("All")
