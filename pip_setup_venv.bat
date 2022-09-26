@echo off
SET mypath=%~dp0
echo Current Path:  %mypath%

set /p env_name= Enter name of venv environment:

cd /d %mypath%

@REM Installs Env from requirements.yml and installs precommit
call python -m venv %env_name%
call %env_name%\Scripts\activate
call pip install requirements.txt
call pre-commit install
call pre-commit autoupdate
call pre-commit install --hook-type commit-msg
call pre-commit install --hook-type pre-push

echo Finished setting up conda env and pre-commit
pause
