@echo off
echo ========================================================
echo VideoGenius AI - Advanced Dependency Resolver
echo ========================================================
echo This script will fix the dependency conflicts between
echo moviepy, numpy, and torch.
echo.

echo Step 1: Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Step 2: Uninstalling conflicting packages...
pip uninstall -y moviepy
pip uninstall -y numpy
pip uninstall -y torch
pip uninstall -y imageio
pip uninstall -y imageio-ffmpeg
pip uninstall -y transformers

echo.
echo Step 3: Installing compatible versions in correct order...
REM Install specific numpy version first
pip install numpy==1.25.0

REM Install latest torch (without specifying version)
pip install torch

REM Install older moviepy version that works with our setup
pip install moviepy==1.0.3 --no-deps
pip install decorator==4.4.2
pip install imageio==2.9.0
pip install imageio-ffmpeg==0.4.7
pip install tqdm==4.64.1
pip install proglog==0.1.10

REM Install transformers for AI models
pip install transformers==4.26.1
pip install gtts==2.3.1

echo.
echo Step 4: Verify components are working...
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import moviepy; print(f'MoviePy version: {moviepy.__version__}')"
python -c "import torch; print(f'Torch version: {torch.__version__}')"
python -c "from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips; print('MoviePy imports working correctly!')"

echo.
echo Step 5: Creating icons...
python create_icons.py

echo.
echo ========================================================
echo Installation Complete
echo ========================================================
echo.
echo Please restart the application by running:
echo     python app.py
echo.
echo If you still experience issues, please try:
echo 1. Deleting the .venv directory and recreating it
echo 2. Running "pip install --upgrade pip setuptools wheel"
echo    before installing other packages
echo.
pause
