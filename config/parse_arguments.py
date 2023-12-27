import argparse


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "--env",
        metavar="--environment",
        type=str,
        required=False,
        default=None,
        help="Environment selected if given",
    )
    parser.add_argument(
        "--verbose",
        metavar="--verbosity",
        type=int,
        required=False,
        default=0,
        help="Verbosity of logging: 0=critical, 1=error, 2=warning, 3=info, 4=debug",
    )
    parser.add_argument(
        "--test",  # Tag to add to the parse
        metavar="--Testing",
        required=False,
        default="Here is a default text",
        help="Returns some helpful information",
    )
    parser.add_argument(  ### -list <item1> <item2>
        "--list",
        metavar="--list",
        nargs="+",
        required=False,
        default=["sample", "list"],
        help="List of search items",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
