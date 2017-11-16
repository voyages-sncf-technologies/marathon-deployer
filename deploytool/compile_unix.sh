#!/usr/bin/env bash

rm -r dist/ build/ __pycache__/
pyinstaller --clean -F --hiddenimport marathon deploytool.py