@echo off
echo === Cyber Survival Game Installation ===
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install pygame
echo Installing pygame...
pip install pygame>=2.1.0

if errorlevel 1 (
    echo.
    echo Installation failed. Please try installing pygame manually:
    echo   pip install pygame
    pause
    exit /b 1
)

echo.
echo === Installation Complete! ===
echo.
echo To play the game, run:
echo   python main.py
echo.
echo Controls:
echo   WASD/Arrow keys: Move
echo   Mouse/Space: Shoot
echo   ESC: Pause
echo   R: Restart (when game over)
echo.
echo Enjoy your cyberpunk survival adventure!
pause 