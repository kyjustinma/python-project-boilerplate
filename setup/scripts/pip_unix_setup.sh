echo Creating Pip env name = $1
python3 -m venv $1
sleep 3
source $1/bin/activate
sleep 1

echo 'Installing requirements.txt...'
pip3 install -r setup/requirements.txt

pre-commit install
pre-commit autoupdate
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push


echo Shell has finished setting up conda env $1 and Pre-Commit and requirements.txt
