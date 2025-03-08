@echo off
echo ========================================================
echo VideoGenius AI - Starting Application
echo ========================================================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Starting the application...
python app.py

echo.
echo If the application didn't start correctly, try running:
echo setup_video.bat
echo.
pause
