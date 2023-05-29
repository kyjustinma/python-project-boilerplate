import os
from platform import platform 
import subprocess
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
        help="Select environment type (conda or pip)",
    )
    parser.add_argument(
        "-os",
        metavar="--operating-system",
        type=str,
        required=False,
        default=None,
        help="inform script if you are using mac or windows",
    )
    args = parser.parse_args()
    return args

def prompt_users(env_type):
  while env_type == None:
    prompt_env=input("Would you like to setup using 'pip' or 'conda'? ")
    if prompt_env.lower().strip() == "pip":
      env_confirmation=input("You have selected Pip3, are you sure? (Y/N) ")
      if (env_confirmation.lower().strip() == "y"):
            env_type = "pip"
      else:
        print("You did not confirm which environment type you wanted, please try again or press Ctrl/CMD + C to exit")
    elif prompt_env.lower().strip() == "conda":
      env_confirmation=input("You have selected Conda, are you sure? (Y/N) ")
      if (env_confirmation.lower().strip() == "y"):
        env_type = "conda"
      else:
        print("You did not confirm which environment type you wanted, please try again or press Ctrl/CMD + C to exit")
  return env_type 


def main():
  print('hello world')
  args = parse_arguments()
  print(os.system)
  env_type = prompt_users(args.env)
  print(env_type)

  if os.system != "nt": # not windows
    process = subprocess.Popen(
      "activate tf2 && python --version" , shell=True,stdout=subprocess.PIPE
    )
    output, error = process.communicate()
  else:
    subprocess.run(["conda activate base","conda env list"])
    process = subprocess.Popen(
      "conda run -n ${CONDA_ENV_NAME} python script.py".split() , stdout=subprocess.PIPE
    )
    output, error = process.communicate()

  print(output)


if __name__ == "__main__":
    main()