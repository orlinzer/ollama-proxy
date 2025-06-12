@echo off

python -m venv .venv
.venv/Script/activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
