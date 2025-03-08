@echo off
echo ========================================================
echo VideoGenius AI - Video Generation Setup
echo ========================================================
echo This script will install all required dependencies
echo to enable video generation functionality.
echo.

echo Step 1: Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Step 2: Installing core video generation packages...
pip install --upgrade pip
echo Installing specific versions of dependencies that work together...
pip install numpy==1.23.5
pip install decorator==4.4.2
pip install tqdm==4.64.1
pip install imageio==2.9.0
pip install imageio-ffmpeg==0.4.7
pip install transformers==4.26.1
REM Latest torch version instead of 1.13.1 which is not available
pip install torch
pip install moviepy==1.0.3
pip install gtts==2.3.1

echo.
echo Step 3: Creating required icons...
python create_icons.py

echo.
echo Step 4: Testing video generation components...
echo Testing MoviePy installation...
python -c "from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips; print('SUCCESS: MoviePy imported correctly')" || echo ERROR: MoviePy import failed.

echo Testing Transformers installation...
python -c "from transformers import pipeline; print('SUCCESS: Transformers imported correctly')" || echo ERROR: Transformers import failed.

echo Testing gTTS installation...
python -c "from gtts import gTTS; print('SUCCESS: gTTS imported correctly')" || echo ERROR: gTTS import failed.

echo.
echo ========================================================
echo Setup Complete! All dependencies installed successfully.
echo ========================================================
echo.
echo Please restart the Flask application by running:
echo     python app.py
echo.
echo Video generation should now work correctly!
echo If you still have issues, check the DEBUG_GUIDE.md file for more help.
echo.
pause
