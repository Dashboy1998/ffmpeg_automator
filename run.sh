#!/bin/bash
set -e

if ! [ -f "python_venv/bin/activate" ]; then
    python -m venv ./python_venv
    source python_venv/bin/activate
    pip install -r "requirements.txt"
else
    source python_venv/bin/activate
fi

source vars.env
python scripts/ffmpeg_automator.py
