echo Creating Conda env name = $1
conda init

conda create --yes --name $1 python=3.10.13
sleep 2

conda activate $1
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


echo Shell has finished setting up conda env $1 with Pre-Commit and requirements.txt

conda activate $1
