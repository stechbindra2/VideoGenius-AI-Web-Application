@echo off
echo =======================================
echo VideoGenius AI - Quick Fix Tool
echo =======================================
echo.
echo This script will fix the "Service Unavailable" error
echo by reinstalling MoviePy and its dependencies.
echo.
pause

echo Step 1: Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Step 2: Uninstalling problematic packages...
pip uninstall -y moviepy
pip uninstall -y imageio
pip uninstall -y imageio-ffmpeg
pip uninstall -y numpy
pip uninstall -y decorator
pip uninstall -y tqdm

echo.
echo Step 3: Installing packages in the correct order...
pip install decorator==4.4.2
pip install numpy==1.23.5
pip install tqdm==4.64.1
pip install imageio==2.9.0
pip install imageio-ffmpeg==0.4.7
pip install moviepy==1.0.3

echo.
echo Step 4: Verifying installation...
python -c "from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip; print('MoviePy imported successfully!')"

echo.
echo Step 5: Create missing icons...
python create_icons.py

echo.
echo Installation complete!
echo Now try generating a video again.
echo If you still have issues, try running:
echo     python reinstall_moviepy.py
echo.
pause
