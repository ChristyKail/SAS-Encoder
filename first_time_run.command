#!/bin/bash

which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    brew update
fi

brew install ffmpeg python-tk@3.9

pip3 install --upgrade pip
pip3 install pandas

cd "$(dirname "$0")" || return
python3 'SAS Encoder UI.py'