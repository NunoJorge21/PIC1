#!/bin/bash

# My Hello, World! script
echo "Running SSM Interface"

sudo apt install python3.8
sudo apt install python3.8-venv
python3 -m venv ssm_env
source ssm_env/bin/activate
sudo apt install pip

pip install plotly==5.22.0
pip install pandas==2.0.3
pip install dash==2.17.1
pip install dash_bootstrap_components==1.6.0
pip install pyserial==3.5

python3 ssm_interface.py