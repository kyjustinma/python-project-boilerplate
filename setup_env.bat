@echo off
SET mypath=%~dp0
echo Current Path:  %mypath%

set /p env_name= Enter name of conda environment:

cd /d %mypath%

@REM Installs Env from requirements.yml and installs precommit
call conda env create --name %env_name% -f requirements.yml
call conda activate %env_name%
call conda install --yes -c conda-forge pre_commit
call pre-commit install

echo Finished setting up conda env and pre-commit
pause
