import logging
import os
import sys
import argparse
import config.settings as settings

__CWD_DIR__ = os.path.abspath(os.getcwd())
__SCRIPT_DIR__ = os.path.dirname(os.path.abspath(__file__))


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "-verbose",
        metavar="--verbosity",
        type=int,
        required=False,
        default=settings.config["VERBOSE"],
        help="Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug",
    )
    parser.add_argument(
        "-t",  # Tag to add to the parse
        metavar="--Help",
        required=False,
        default="Here is a default text",
        help="Returns help information",
    )
    parser.add_argument(
        "-d",
        metavar="--directory",
        required=False,
        default=__CWD_DIR__,
        help="Prints the current directory",
    )
    parser.add_argument(
        "-s",
        metavar="--script",
        required=False,
        default=__SCRIPT_DIR__,
        help="Prints the script's directory",
    )
    parser.add_argument(  ### -list <item1> <item2>
        "-list",
        metavar="--list",
        nargs="+",
        required=False,
        default=["sample", "list"],
        help="List of search items",
    )

    args = parser.parse_args()

    # verbose = {
    #     0: logging.CRITICAL,
    #     1: logging.ERROR,
    #     2: logging.WARNING,
    #     3: logging.INFO,
    #     4: logging.DEBUG,
    # }
    # logging.basicConfig(
    #     format="%(asctime)s | [%(levelname)5s][%(filename)20s] | %(message)s",
    #     level=verbose[args.verbose],
    #     stream=sys.stdout,
    # )
    # logging.info(f"Logging level is at {args.verbose}")

    return args


def main():
    logging.info(f"Current Directory {args.d}")
    logging.info(f"Script Directory {args.s}")
    pass


if __name__ == "__main__":
    args = parse_arguments()
    main()
