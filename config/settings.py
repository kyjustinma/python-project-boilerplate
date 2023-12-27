"""
This file is used to store any global variables such as file paths etc
"""
import os
import sys
import logging
import yaml
import socket

import logging.config
from dotenv import dotenv_values
from .logging_utils import ColouredLoggingFormatter
from .parse_arguments import parse_arguments


dotenv_config = dotenv_values(".env")
file_path = os.path.dirname(os.path.realpath(__file__))


# ==============================================================================================================
### Manage Logging Functions
# ==============================================================================================================
def create_data_folder():
    data_path = os.path.join(os.path.dirname(file_path), "data")
    sub_folders = ["logs", "csv", "images", "json", "models", "database"]
    sub_folder_paths = [os.path.join(data_path, folder) for folder in sub_folders]
    for paths in sub_folder_paths:
        if not os.path.exists(paths):
            os.makedirs(paths)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("[Uncaught exception]:", exc_info=(exc_type, exc_value, exc_traceback))


def logger_init(name):
    logging_yaml_path = os.path.join(file_path, "prefixed_logger_setting.yaml")
    # logging_yaml_path = os.path.join(file_path, "logger_setting.yaml")
    with open(logging_yaml_path, "r") as f:
        yaml_config = yaml.full_load(f)
        logging.config.dictConfig(config=yaml_config)

    logger = logging.getLogger(name=name)
    coloured_handler = logging.StreamHandler()
    coloured_handler.setFormatter(
        ColouredLoggingFormatter(
            yaml_config=yaml_config,
            logger_name=name,
        )
    )
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)  # Remove the yaml logger (no colour)
    logger.addHandler(coloured_handler)  # Add colour logger
    sys.excepthook = handle_exception  # Exception handler
    return logger


# ==============================================================================================================
### Manage global variables under "env_config"
# ==============================================================================================================
def env_get(variable_name: str, default: str, type: str = str) -> None:
    """env_get
    Get values from the .ENV file
    Args:
        variable_name (str): .ENV name
        default (str): default value if not defined
        type (str, optional): Expected type for the .ENV variable. Defaults to string.
    """
    env_config[variable_name] = type(dotenv_config.get(variable_name, default))
    try:
        if env_config[variable_name] is not None:
            logger.info(
                f"[.env] Setting '{variable_name}' to '{env_config[variable_name]}'"
            )
        else:
            logger.warning(
                f"[.env] MISSING '{variable_name}' - Setting to '{env_config[variable_name]}'"
            )
    except Exception as e:
        if env_config[variable_name] is not None:
            print(
                f"\t\t\t\t [.env] Setting '{variable_name}' to '{env_config[variable_name]}'"
            )
        else:
            print(
                f"\t\t\t\t [.env] MISSING '{variable_name}' - Setting to '{env_config[variable_name]}'"
            )


def global_variable_mappings(config: dict):
    """mappings


    Args:
        config (dict): _description_
    """
    mapping = {0: "Text0", 1: "Text1", 2: "Text2", 3: "Text3"}
    config["TEST_MAPPING"] = mapping
    config["WHEEL_CMD"] = [
        "List",
        "Example",
        "For",
        "Template",
    ]


def args_to_config(config: dict):
    """args_to_config _summary_

    Args:
        config (dict): _description_
    """
    args = parse_arguments()
    config.update(vars(args))
    pass


# ==============================================================================================================
### Add other useful functions on startup below
# ==============================================================================================================
def get_ip():
    host_name = socket.gethostname()
    __HOST__ = socket.gethostbyname(host_name).strip()
    return __HOST__.strip()


# ==============================================================================================================
### Initialisation Sequence
# ==============================================================================================================
def __init__():  # On initialisation
    print(
        "\n\n\n\n======================================== config.settings.py Setup ============================================"
    )
    # Create global variables if needed
    global logger
    global env_config
    env_config = {}

    create_data_folder()  # creates the data folders for logging
    env_get("LOGGING_LEVEL", default="ALL", type=str)
    logger = logger_init(env_config["LOGGING_LEVEL"])

    logger.info(f"Current logging level set to '{env_config['LOGGING_LEVEL']}'")
    global_variable_mappings(env_config)
    ### ========================================================================
    ### Add .ENV variables here (overwrite mappings)
    env_get("TEST_ENV_STRING", default="DEFAULT_SETTING", type=str)
    env_get("TEST_ENV_STRING2", default="DEFAULT_TEST_ENV_STRING2", type=str)

    ### ========================================================================
    args_to_config(env_config)  # Arguments overwrites all Environment variables
    print(
        "======================================== Settings complete ====================================================\n\n\n\n"
    )
