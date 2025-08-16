#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt py2app
python3 -m pip install scipy
python3 -m pip install opencv-python
pip3 install scipy
python setup.py py2app
