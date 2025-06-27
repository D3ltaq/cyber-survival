#!/bin/bash

echo "=== Cyber Survival Game Installation ==="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available. Please install pip for Python 3."
    exit 1
fi

echo "pip3 found: $(pip3 --version)"
echo ""

# Install pygame
echo "Installing pygame..."
pip3 install pygame>=2.1.0

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Installation Complete! ==="
    echo ""
    echo "To play the game, run:"
    echo "  python3 main.py"
    echo ""
    echo "Controls:"
    echo "  WASD/Arrow keys: Move"
    echo "  Mouse/Space: Shoot"
    echo "  ESC: Pause"
    echo "  R: Restart (when game over)"
    echo ""
    echo "Enjoy your cyberpunk survival adventure!"
else
    echo ""
    echo "Installation failed. Please try installing pygame manually:"
    echo "  pip3 install pygame"
fi 