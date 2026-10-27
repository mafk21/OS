#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ -x ".venv/bin/python3" ]; then
  exec ".venv/bin/python3" main.py
else
  exec python3 install_jarvis.py --install --launch
fi
