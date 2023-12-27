echo Creating Pip env name = $1 using $2

$2 -m venv $1 # python -m venv venv
sleep 2

source $1/bin/activate
sleep 1

echo Installing requirements.txt...
pip3 install --no-input -r setup/requirements.txt
pip3 install --no-input pre-commit
pip3 install --no-input python-dotenv
pip3 install --no-input PyYAML
sleep 1

pre-commit install
pre-commit autoupdate
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push

echo Shell has finished setting up conda env $1 and Pre-Commit and requirements.txt

source $1/bin/activate
