#!/bin/bash

# 取得目前的工作目錄
PWD=$(pwd)

echo "Start to create virtual environment and install dependencies..."
echo ""

# 如果 .venv 目錄存在，就啟動虛擬環境並安裝相依套件
# 否則建立虛擬環境並安裝相依套件
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -U pip setuptools pip-autoremove
    pip install -r requirements.txt
else
    python3.10 -m venv .venv
    source .venv/bin/activate
    pip install -U pip setuptools pip-autoremove
    pip install -r requirements.txt
fi

deactivate

echo ""
echo "Finished!"