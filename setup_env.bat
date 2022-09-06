@echo off
SET mypath=%~dp0
echo Current Path:  %mypath%

set /p env_name= Enter name of conda environment:

cd /d %mypath%
start cmd.exe /k "conda env create --name %env_name% -f requirements.yml && conda activate %env_name% && conda install --yes -c conda-forge pre_commit && pre-commit install"
