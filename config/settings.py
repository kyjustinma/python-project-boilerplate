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


def create_data_folder():
    data_path = os.path.join(os.path.dirname(file_path), "data")
    sub_folders = ["logs", "csv", "images", "json", "models"]
    sub_folder_paths = [os.path.join(data_path, folder) for folder in sub_folders]
    for paths in sub_folder_paths:
        if not os.path.exists(paths):
            os.makedirs(paths)


def logger_init(name):
    logging_yaml_path = os.path.join(file_path, "logger_setting.yaml")
    with open(logging_yaml_path, "r") as f:
        yaml_config = yaml.full_load(f)
        logging.config.dictConfig(yaml_config)
    logger = logging.getLogger(name=name)
    return logger


def __init__():  # On initialisation
    print(
        "\n\n ======================================== config.settings.py ========================================"
    )
    global config
    config = {}
    create_data_folder()
    env_get("LOGGING_LEVEL", default="All", type=str)

    global logger
    logger = logger_init(config["LOGGING_LEVEL"])
    logger.info(f"Current logging level at {config['LOGGING_LEVEL']}")

    ### Insert all other ENV variables below
    env_get("VERBOSE", default=3, type=int)
    env_get("FLASK_PORT", default=8080, type=int)
    env_get("FLASK_IP", default=get_ip(), type=str)

    mappings()

    print(
        " ======================================== config.settings.py ========================================\n\n"
    )


def env_get(variable_name: str, default: str, type: str = "string") -> str or float:
    try:
        if type != "string":
            config[variable_name] = type(env_config[variable_name])
        else:
            config[variable_name] = env_config[variable_name]
    except Exception as e:
        if variable_name == "LOGGING_LEVEL":
            print(f"\t\t[.env] Missing '{variable_name}' setting to '{default}'")
        else:
            logger.warning(f"[.env] Missing '{variable_name}' setting to '{default}'")
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
