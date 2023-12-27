# Python Project Template

## About The Project

This is a template that uses both Conda / Pip and Pre-commit, to ensure that everyone in the team has the same environment running on their device.

Pre-commit is used to ensure that certain commit standards are enforced.

## Built With

[![python][python3.10.13-shield]][python3.10.13-url]
[![conda][conda-forge-shield]][conda-forge-url]

This template is primary focused on Python 3.10.13 with Anaconda (using Conda-forge)

# Getting Started

## Installation Prerequisites

- [Python 3.10.13][python3.10.13-url]
- [Anaconda][conda-forge-url] \* Optional

## Setup Perquisite

1. Move **YOUR** _requirements.txt_ (pip) or _requirements.yaml_ (Conda) into `setup/requirements`
2. Open the project directory in Command Line / Terminal and Run the batch file in setup accordingly

### Windows:

**Pip3** install

```
setup\conda_setup_venv.bat
```

**Conda** install

```
setup\pip_setup_venv.bat
```

### MacOS / Linux:

**Pip3** install

```
setup/conda_setup_venv.bat
```

**Conda** install

```
setup/pip_setup_venv.bat
```

1. You will be prompted to enter the `<env_name>`, please select a suitable name and ensure that the environment does not already exist
2. The environment will be installed **THEN** `pre-commit` will also be installed.
3. The base requirements.txt venv comes with the below as standard
   - black
   - python-dotenv
   - PyYAML
   - pre-commit - installed and applied after via command line

# Using Pre-Commit

To effectively use the template with Pre-Commit you have to ensure that your custom env is setup with the [Pre-commit library](https://pre-commit.com/) (Should be automatically installed):

1. Ensure that your newly created python environment is active

   **Conda** env

   ```
   conda activate <env_name>
   ```

   **Pip3** venv

   ```
   <env_name>\Scripts\activate
   ```

2. Check that pre-commit is installed properly on your virtual environment

   ```
   pip list
   ```

   Should have the pre-commit package and its version

   ```
   ...
   pre-commit     x.x.x
   ...
   ```

3. If precommit is installed then run
   ```
   pre-commit install
   pre-commit autoupdate
   pre-commit install --hook-type commit-msg
   pre-commit install --hook-type pre-push
   ```

# Working as a team with Git

1. Each person should create their own branch according to feature (`git checkout -b feature/<AmazingNewFeature>`)
2. Following the commit message format of (`git commit -a '<prefix>:<informative commit message>'`)
   ```
   prefix must follow the following
   build | ci | docs | feat | fix | perf | refactor | style | test | chore | revert | bump
   ```

To learn more about the basics of git click here: <span style="font-size:2em;">[Git basics](GIT_PRECOMMIT.md)</span>

# Roadmap

## Features

- [ ] Implement **init**.py into template
- [ ] Add docker compile template
- [ ] ReadMe for each of the files within the template

## Bugs

Please raise any bugs found to me, Thank you.

[python3.10.13-shield]: https://img.shields.io/badge/Python-3.10.13-brightgreen
[python3.10.13-url]: https://www.python.org/downloads/release/python-31013/
[conda-forge-shield]: https://img.shields.io/conda/dn/conda-forge/python?label=Anaconda
[conda-forge-url]: https://www.anaconda.com/products/distribution
