#!/bin/bash

echo "Checking dependencies..."
apt install python3.12 python3.12-venv

echo "Creating python 3.12 environment..."
python3.12 -m venv .venv

source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Finished"