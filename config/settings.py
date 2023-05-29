"""
This file is used to store any global variables such as file paths etc
"""
import os
import sys
import socket
import logging
import logging.config
import yaml
from .parse_arguments import parse_arguments

from dotenv import dotenv_values

env_config = dotenv_values(".env")
file_path = os.path.dirname(os.path.realpath(__file__))


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("[Uncaught exception]:", exc_info=(exc_type, exc_value, exc_traceback))


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
    sys.excepthook = handle_exception
    return logger


def mappings():
    # Place global variables here
    mapping = {0: "Text0", 1: "Text1", 2: "Text2", 3: "Text3"}
    config["TEST_MAPPING"] = mapping
    config["WHEEL_CMD"] = [
        "List",
        "Example",
        "For",
        "Template",
    ]


def args_to_config():
    args = parse_arguments()
    config.update(vars(args))
    pass


def __init__():  # On initialisation
    print(
        "\n\n ======================================== config.settings.py Setup ========================================"
    )
    # Create global variables if needed
    global config
    config = {}
    create_data_folder()  # creates the data folders for logging
    env_get("LOGGING_LEVEL", default="All", type=str)
    global logger
    logger = logger_init(config["LOGGING_LEVEL"])
    logger.info(f"Current logging level at {config['LOGGING_LEVEL']}")
    mappings()
    ### ========================================================================
    ### Add .ENV variables here (overwrite mappings)
    env_get("TEST_ENV_STRING", default="DEFAULT_SETTING", type=str)

    ### ========================================================================
    args_to_config()
    print(
        " ======================================== Settings complete ========================================\n\n"
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


# ==============================================================================================================
### Add other useful functions on startup below
# ==============================================================================================================
def get_ip():
    host_name = socket.gethostname()
    __HOST__ = socket.gethostbyname(host_name).strip()
    return __HOST__.strip()
