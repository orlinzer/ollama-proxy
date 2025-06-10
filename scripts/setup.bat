@echo off

python -m venv .venv
.venv/Script/activate
pip install --upgrade pip
pip install -r requirements.txt
