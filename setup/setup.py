import os
import platform
import subprocess, shlex
import argparse

cwd = os.getcwd()


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "-env",
        metavar="--environment",
        type=str,
        required=False,
        default=None,
        help="Select environment type (Conda or Pip)",
    )
    parser.add_argument(
        "-os",
        metavar="--operating-system",
        type=str,
        required=False,
        default=None,
        help="Inform script if you are using Mac or Windows",
    )
    parser.add_argument(
        "-name",
        metavar="--environment-name",
        type=str,
        required=False,
        default="venv",
        help="Tell the setup the name of the environment name",
    )
    args = parser.parse_args()
    return args


def prompt_users(env_type):
    while env_type == None:
        prompt_env = input("Would you like to setup using 'pip' or 'conda'? ")
        if prompt_env.lower().strip() == "pip":
            env_confirmation = input("You have selected Pip3, are you sure? (Y/N) ")
            if env_confirmation.lower().strip() == "y":
                env_type = "pip"
            else:
                print(
                    "You did not confirm which environment type you wanted, please try again or press Ctrl/CMD + C to exit"
                )
        elif prompt_env.lower().strip() == "conda":
            env_confirmation = input("You have selected Conda, are you sure? (Y/N) ")
            if env_confirmation.lower().strip() == "y":
                env_type = "conda"
            else:
                print(
                    "You did not confirm which environment type you wanted, please try again or press Ctrl/CMD + C to exit"
                )
    return env_type


def main():
    args = parse_arguments()
    env_type = prompt_users(args.env)  # pip / conda
    os_type = os.name  # 'nt' = windows , 'posix' = mac
    env_name = args.name
    print(
        f"New '{env_type}' environment will be created with name '{env_name}' on '{platform.platform()}'"
    )

    if "nt" in os_type:  # not windows
        ### TODO auto build env for windows
        process = subprocess.Popen(
            "activate tf2 && python --version", shell=True, stdout=subprocess.PIPE
        )
        output, error = process.communicate()
    elif "posix" in os_type:
        if "conda" in env_type:
            process = subprocess.Popen(
                [f"source setup/scripts/conda_unix_setup.sh {env_name}"],
                shell=True,
                stdout=subprocess.PIPE,
            )
        elif "pip" in env_type:
            process = subprocess.Popen(
                [f"source setup/scripts/pip_unix_setup.sh {env_name}"],
                shell=True,
                stdout=subprocess.PIPE,
            )
        output, error = process.communicate()
        output = output.decode("utf-8")
        print(output)
        if error is not None:
            print(f"ERROR: {error.decode('utf-8')}")

    else:
        print(f"Unknown OS name {os_type}:{platform.platform()}")

    print("End of setup.py script")


if __name__ == "__main__":
    main()
