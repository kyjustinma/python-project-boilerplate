@echo off

echo Creating Conda env name = %1
call conda init
call conda create --name %1 python=3.10.13
timeout /t 2 /nobreak

call conda activate %1
timeout /t 1 /nobreak

echo Installing requirements.txt...
call pip install --no-input -r setup\requirements.txt
call pip install --no-input pre-commit
call pip install --no-input python-dotenv
call pip install --no-input PyYAML
timeout /t 1 /nobreak

call pre-commit install
call pre-commit autoupdate
call pre-commit install --hook-type commit-msg pre-push

echo Bash has finished setting up Conda env %1 with Pre-Commit and requirements.txt

call conda activate %1
