#!/bin/bash

# Setup script to create a virtual environment matching the working setup
echo "Setting up virtual environment for SPCA Maps..."

# Check if Python 3.9 is available
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Warning: Using python3 instead of python3.9"
else
    echo "Error: Python 3 not found. Please install Python 3.9 or later."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install exact package versions
echo "Installing packages with exact versions..."
pip install -r requirements.txt

echo "Virtual environment setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the app, run: streamlit run app.py" 