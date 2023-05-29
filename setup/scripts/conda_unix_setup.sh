echo Creating Conda env name = $1
conda init

sleep 1
conda create --yes --name $1 python=3.8.13
conda activate $1
sleep 1

echo 'Installing requirements.txt...'
pip install -r setup\requirements\requirements.txt

pre-commit install
pre-commit autoupdate
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push


echo Shell has finished setting up conda env $1 and Pre-Commit and requirements.txt
