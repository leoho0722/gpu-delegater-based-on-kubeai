#!/bin/bash

# Check if virtual environment exists
function check_venv {
    if [ -d ".venv" ]; then
        echo "Virtual environment already exists..."
    else
        echo "Virtual environment not found..."
        exit 0
    fi
}

check_venv

# Check if backend directory exists
function check_backend {
    if [ -d "backend" ]; then
        echo "Backend directory already exists..."
    else
        echo "Backend directory not found..."
        exit 0
    fi
}

check_backend

# Start the server

function start_server {
    cd backend

    if [ -d "logs" ]; then
        echo "Logs directory already exists..."
    else
        mkdir logs
    fi

    PYTHON_BIN=$(which python3)
    nohup $PYTHON_BIN server.py > logs/server.log 2>&1 &
}

start_server