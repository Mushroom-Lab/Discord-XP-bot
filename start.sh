#!/bin/bash
source venv/bin/activate
nohup python3.7 -u main.py > Logs/logs.txt 2>&1 &