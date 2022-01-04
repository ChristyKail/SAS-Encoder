#!/bin/bash
pip3 install pandas
brew install ffmpeg python-tk@3.9
cd "$(dirname "$0")" || return
python3 'SAS Encoder UI.py'