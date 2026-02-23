#!/bin/bash
# This script assumes you are running Windows with docker installed and a localstack auth key under LS_AUTH_TOKEN. Additional work is needed to make it compatible with mac & linux.

# Setup python env
python -m venv .venv
pip install -r requirements.txt
source .venv/Scripts/activate

# Stand up temporal and localstack environments
docker-compose up -d