#!/bin/bash

# Set variables
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
APP_MODULE="triptracks.wsgi:application"
BIND_ADDRESS="0.0.0.0:8000"

# Check if virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv $VENV_DIR
    echo "Virtual environment created."
fi

# Activate the virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source $VENV_DIR/bin/activate  # Linux/macOS
else
    source $VENV_DIR/Scripts/activate  # Windows
fi

echo "Virtual environment activated."

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements..."
    pip install -r $REQUIREMENTS_FILE
    echo "Requirements installed."
else
    echo "Requirements file not found. Skipping installation."
fi

# Set the ENV environment variable
export ENV="DEV"
echo "Environment variable ENV set to $ENV."

# Start the server using Waitress
echo "Starting the Waitress server..."
waitress-serve --listen=$BIND_ADDRESS $APP_MODULE
