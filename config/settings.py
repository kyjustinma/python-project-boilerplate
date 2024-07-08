"""
This file is used to store any global variables such as file paths etc
"""

import argparse
import os
import sys
import logging
from typing import Literal
import yaml
import socket
import ast

import logging.config
from dotenv import dotenv_values
from .logging_utils import ColouredLoggingFormatter, PrefixedTimedRotatingFileHandler
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
    logger.critical(
        "[Uncaught exception]:", exc_info=(exc_type, exc_value, exc_traceback)
    )


def __get_yaml_format(yaml_dict: dict, logger_name="ALL") -> str:
    yaml_format = None
    for valid_handlers in [
        yaml_handlers
        for yaml_handlers in yaml_dict["handlers"]
        if "console" in yaml_handlers.lower()
    ]:
        if (
            yaml_dict["handlers"][valid_handlers]["level"]
            == yaml_dict["loggers"][logger_name]["level"]
        ):
            formatter_type = yaml_dict["handlers"][valid_handlers]["formatter"]
            yaml_format = yaml_dict["formatters"][formatter_type]["format"]
            break
    return yaml_format


def logger_init(
    name: str,
    colour_logging_level: Literal[None, "Level", "Line"] = None,
):
    logging_yaml_path = os.path.join(file_path, "prefixed_logger_setting.yaml")
    # logging_yaml_path = os.path.join(file_path, "logger_setting.yaml")
    with open(logging_yaml_path, "r") as f:
        yaml_config = yaml.full_load(f)

    logging.config.dictConfig(config=yaml_config)
    logger = logging.getLogger(name=name)
    logging.root.setLevel(logger.level)

    if colour_logging_level is not None:
        coloured_handler_fmt = __get_yaml_format(yaml_config, name)
        if coloured_handler_fmt is not None:
            coloured_handler = logging.StreamHandler()
            coloured_handler.name = "coloured_console"
            coloured_handler.setFormatter(
                ColouredLoggingFormatter(
                    fmt=coloured_handler_fmt, colour_level=colour_logging_level
                )
            )
            for handler in logger.handlers[:]:
                # Removes the current console handler replaces with coloured
                if "console" in str(handler.name):
                    logger.removeHandler(handler)  # Remove the yaml logger (no colour)
            logger.addHandler(coloured_handler)  # Add colour logger

    sys.excepthook = handle_exception  # Exception handler
    return logger


def getCustomLogger(
    logger_name: str,
    logging_level=logging.DEBUG,
    colour_logging_level: Literal[None, "Level", "Line"] = "Level",
    text_colour: str = None,
):
    level_converter = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def adjust_logger_fmt(fmt: str) -> str:
        logger_name_fmt = fmt
        if " | " in fmt:
            logger_name_fmt = fmt.replace(" | ", f" | [{logger_name}]", 1)
        return logger_name_fmt

    logging_yaml_path = os.path.join(file_path, "prefixed_logger_setting.yaml")
    with open(logging_yaml_path, "r") as f:
        yaml_config = yaml.full_load(f)

    custom_logger = logging.getLogger(logger_name)
    for handler_type in [
        "debug_file_handler",
        "info_file_handler",
        "warning_file_handler",
        "error_file_handler",
        "critical_file_handler",
    ]:
        file_type = handler_type.split("_file_handler")[0]
        handler_formatter = yaml_config["handlers"][handler_type]["formatter"]
        handler_level = yaml_config["handlers"][handler_type]["level"]
        PreFixTimeHandlerArgs = {
            "filename": yaml_config["handlers"][handler_type]["filename"].replace(
                f"{file_type}.log", logger_name + f"_{file_type}.log"
            ),
            "when": yaml_config["handlers"][handler_type]["when"],
            "interval": yaml_config["handlers"][handler_type]["interval"],
            "backupCount": yaml_config["handlers"][handler_type]["backupCount"],
            "encoding": yaml_config["handlers"][handler_type]["encoding"],
        }
        file_handler = PrefixedTimedRotatingFileHandler(**PreFixTimeHandlerArgs)
        file_handler.setFormatter(
            logging.Formatter(
                adjust_logger_fmt(
                    yaml_config["formatters"][handler_formatter]["format"]
                )
            )
        )
        file_handler.setLevel(level_converter[handler_level])
        file_handler.name = handler_type
        custom_logger.addHandler(file_handler)

    coloured_handler = logging.StreamHandler(sys.stdout)
    if colour_logging_level is not None:
        coloured_handler_fmt = adjust_logger_fmt(
            __get_yaml_format(yaml_config, ENV_CONFIG["LOGGING_LEVEL"])
        )
        coloured_handler = logging.StreamHandler(sys.stdout)
        coloured_handler.setLevel(logging_level)
        coloured_handler.name = "coloured_console"
        coloured_handler.setFormatter(
            ColouredLoggingFormatter(
                fmt=coloured_handler_fmt,
                colour_level=colour_logging_level,
                colour_logger_name=(logger_name, text_colour),
            )
        )
    else:
        coloured_handler.setFormatter(
            logging.Formatter(
                adjust_logger_fmt(
                    yaml_config["formatters"][handler_formatter]["format"]
                )
            )
        )
    custom_logger.addHandler(coloured_handler)  # Add colour logger
    return custom_logger


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


def env_get(variable_name: str, variable_type: type = str, default: str = None) -> None:
    """env_get
    Get values from the .ENV file
    Args:
        variable_name (str): .ENV name
        default (str): default value if not defined
        type (str, optional): Expected type for the .ENV variable. Defaults to string.
    """
    env_value = ENV_CONFIG.get(variable_name, None)  # Get config if it exists
    if env_value == None and default is None:
        raise Exception(
            f"Failed to start program as .ENV Variable [{variable_name}] was not defined and no default value was given."
        )

    if not isinstance(default, variable_type):  # Default is incorrect type
        message = f"\n\n .[.env] Variable ({variable_name}) Default Value ({default}) does not match Default Type ({variable_type})\n"
        try:
            logger.error(message)
        except Exception:
            print(message)
        raise Exception(message)

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
    logger = logger_init(ENV_CONFIG["LOGGING_LEVEL"], colour_logging_level="Level")
    logger.info(f"Current logging level set to '{ENV_CONFIG['LOGGING_LEVEL']}'")
    global_variable_mappings(ENV_CONFIG)
    ### ========================================================================
    ### Add .ENV variables here (overwrite mappings)
    env_get("TEST_ENV_STRING", default="DEFAULT_SETTING", variable_type=str)
    env_get("TEST_ENV_STRING2", default="test", variable_type=str)

    ### ========================================================================
    ENV_CONFIG.update(vars(args))  # Arguments overwrites all Environment variables
    ENV_CONFIG = MappingProxyType(ENV_CONFIG)
    print(
        "======================================== Settings complete ====================================================\n"
    )
