"""
This file is used to store any global variables such as file paths etc
"""
import os
import time
import typing
import socket

from dotenv import dotenv_values

env_config = dotenv_values(".env")


def __init__():  # On initialisation
    print("")
    global config
    config = {}

    ### Getting ENV from dotenv
    env_get("VERBOSE", default=3, type=int)
    env_get("FLASK_PORT", 8080, type=int)
    env_get("FLASK_IP", get_ip())

    mappings()
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
