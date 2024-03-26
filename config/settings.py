"""
This file is used to store any global variables such as file paths etc
"""
import argparse
import os
import sys
import logging
import yaml
import socket
import ast

import logging.config
from dotenv import dotenv_values
from .logging_utils import ColouredLoggingFormatter
from .parse_arguments import parse_arguments
from types import MappingProxyType


file_path = os.path.dirname(os.path.realpath(__file__))


# ==============================================================================================================
### Manage Logging Functions
# ==============================================================================================================
def create_data_folder():
    data_path = os.path.join(os.path.dirname(file_path), "data")
    sub_folders = ["config", "logs", "csv", "images", "json", "models", "database"]
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
        # Removes the current console handler replaces with coloured
        if "console" in str(handler.name):
            logger.removeHandler(handler)  # Remove the yaml logger (no colour)
    logger.addHandler(coloured_handler)  # Add colour logger
    sys.excepthook = handle_exception  # Exception handler
    return logger


# ==============================================================================================================
### Manage global variables under "env_config"
# ==============================================================================================================
def load_dot_env(args: argparse.Namespace):
    func_name = sys._getframe(0).f_code.co_name
    dot_env_path = os.path.normpath(f"environments/{args.env}.env")
    try:
        if os.path.exists(dot_env_path):
            dotenv_config = dotenv_values(dot_env_path)
            print(
                f"\t\t\t\t   [settings - {func_name}] | Loaded {args.env} from {dot_env_path}"
            )
        else:
            dotenv_config = dotenv_values(".env")
            print(f"\t\t\t\t   [settings - {func_name}] | Loaded .env from .env")
    except Exception as e:
        print(f"An error has occurred while loading {dot_env_path}: {e}")
        dotenv_config = dotenv_values(".env")  # Safest
    return dotenv_config


def env_get(variable_name: str, default: str, variable_type: type = str) -> None:
    """env_get
    Get values from the .ENV file
    Args:
        variable_name (str): .ENV name
        default (str): default value if not defined
        type (str, optional): Expected type for the .ENV variable. Defaults to string.
    """
    if not isinstance(default, variable_type):  # Default is incorrect type
        message = f"\n\n .[.env] Variable ({variable_name}) Default Value ({default}) does not match Default Type ({variable_type})\n"
        try:
            logger.error(message)
        except Exception:
            print(message)
        raise Exception(message)

    env_value = ENV_CONFIG.get(variable_name, None)  # Get config if it exists
    if env_value is None:
        ENV_CONFIG[variable_name] = default
        message = f"[.env] MISSING '{variable_name}' - Setting to default {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
        try:
            logger.error(message)  # Using Default
        except Exception:
            print("\t\t\t\t   ", message)
        return

    if not isinstance(env_value, variable_type):
        # try:
        env_value = ast.literal_eval(env_value)
        # except Exception:
        if not isinstance(env_value, variable_type):
            ENV_CONFIG[variable_name] = default
            message = f"[.env] '{variable_name}' has incorrect Type ({variable_type}) - Setting to default {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
            try:
                logger.error(message)
            except Exception:
                print("\t\t\t\t   ", message)
            return

    ENV_CONFIG[variable_name] = env_value
    message = f"[.env] Setting '{variable_name}' to {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
    try:
        if env_value is not None:
            logger.info(
                f"[.env] Setting '{variable_name}' to {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
            )
        else:
            logger.warning(
                f"[.env] MISSING '{variable_name}' - Setting to {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
            )
    except Exception as e:
        if env_value is not None:
            print(
                f"\t\t\t\t   [.env] | Setting '{variable_name}' to {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
            )
        else:
            print(
                f"\t\t\t\t   [.env] | MISSING '{variable_name}' - Setting to {type(ENV_CONFIG[variable_name])}:'{ENV_CONFIG[variable_name]}'"
            )


def global_variable_mappings(env_config: dict):
    """mappings


    Args:
        config (dict): _description_
    """
    mapping = {0: "Text0", 1: "Text1", 2: "Text2", 3: "Text3"}
    env_config["TEST_MAPPING"] = mapping
    env_config["WHEEL_CMD"] = [
        "List",
        "Example",
        "For",
        "Template",
    ]


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
    create_data_folder()  # Creates the data folders for logging

    global logger
    global ENV_CONFIG

    args = parse_arguments()  # Get input arguments
    ENV_CONFIG = load_dot_env(args=args)

    env_get("LOGGING_LEVEL", default="ALL", variable_type=str)
    logger = logger_init(ENV_CONFIG["LOGGING_LEVEL"])
    logger.info(f"Current logging level set to '{ENV_CONFIG['LOGGING_LEVEL']}'")
    global_variable_mappings(ENV_CONFIG)
    ### ========================================================================
    ### Add .ENV variables here (overwrite mappings)
    env_get("TEST_ENV_STRING", default="DEFAULT_SETTING", variable_type=str)
    env_get("TEST_ENV_STRING2", default="DEFAULT_TEST_ENV_STRING2", variable_type=str)

    ### ========================================================================
    ENV_CONFIG.update(vars(args))  # Arguments overwrites all Environment variables
    ENV_CONFIG = MappingProxyType(ENV_CONFIG)
    print(
        "======================================== Settings complete ====================================================\n"
    )
