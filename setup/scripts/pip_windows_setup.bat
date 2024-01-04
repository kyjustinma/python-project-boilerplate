@echo off

echo Creating Pip env name = %1
call python -m venv %1
timeout /t 2 /nobreak

call %1\Scripts\activate
timeout /t 1 /nobreak

echo Installing requirements.txt...
call pip install --no-input -r setup\requirements.txt
call pip install --no-input pre-commit
call pip install --no-input python-dotenv
call pip install --no-input PyYAML
timeout /t 1 /nobreak

call pre-commit install
call pre-commit autoupdate
call pre-commit install --hook-type commit-msg
call pre-commit install --hook-type pre-push

echo Bash has finished setting up Pip env %1 with Pre-Commit and requirements.txt
pauses

call %1\Scripts\activate