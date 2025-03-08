"""
Debug tool for the VideoGenius AI application.
This script helps diagnose issues with the video generation process.
"""

import os
import sys
import traceback
import shutil
import json
from pathlib import Path

def check_directories():
    """Check if all required directories exist and are accessible."""
    dirs_to_check = ['uploads', 'static/output', 'static/images', 'temp_files']
    print("\nChecking directories...")
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            try:
                # Try to create a test file
                test_file = os.path.join(dir_path, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[OK] Directory '{dir_path}' exists and is writable")
            except Exception as e:
                print(f"[ERROR] Directory '{dir_path}' exists but is not writable: {e}")
        else:
            try:
                os.makedirs(dir_path)
                print(f"[OK] Created directory '{dir_path}'")
            except Exception as e:
                print(f"[ERROR] Could not create directory '{dir_path}': {e}")

def check_session(session_id=None):
    """Check session directory and files."""
    if session_id is None:
        # Find the most recent session directory
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            print("\n[ERROR] Uploads directory does not exist.")
            return
        
        sessions = [d for d in os.listdir(upload_dir) 
                    if os.path.isdir(os.path.join(upload_dir, d))]
        
        if not sessions:
            print("\n[ERROR] No session directories found.")
            return
        
        # Get the most recent session
        latest_session = max(sessions, 
                            key=lambda s: os.path.getctime(os.path.join(upload_dir, s)))
        session_id = latest_session
    
    session_dir = os.path.join('uploads', session_id)
    print(f"\nChecking session directory: {session_dir}")
    
    if not os.path.exists(session_dir):
        print(f"[ERROR] Session directory does not exist: {session_dir}")
        return
    
    # Check for image files
    image_files = [f for f in os.listdir(session_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"[ERROR] No image files found in session directory.")
    else:
        print(f"[OK] Found {len(image_files)} image files")
        
        # Check if images can be opened
        try:
            from PIL import Image
            for img_file in image_files[:2]:  # Check first 2 images
                img_path = os.path.join(session_dir, img_file)
                try:
                    with Image.open(img_path) as img:
                        print(f"[OK] Image is valid: {img_file} ({img.format}, {img.size}px)")
                except Exception as e:
                    print(f"[ERROR] Failed to open image {img_file}: {e}")
        except ImportError:
            print("[SKIP] PIL/Pillow not available to check image validity")

def test_video_creation():
    """Test the video creation process with minimal requirements."""
    print("\nTesting minimal video creation...")
    
    try:
        # Create a test directory with sample image
        test_dir = "debug_test_video"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create a simple test image
        try:
            from PIL import Image, ImageDraw
            for i in range(2):
                img = Image.new('RGB', (640, 360), color=(73, 109, 137))
                draw = ImageDraw.Draw(img)
                draw.rectangle([100, 100, 540, 260], fill=(255, 255, 255))
                draw.text((320, 180), f"Test Image {i+1}", fill=(0, 0, 0))
                img.save(os.path.join(test_dir, f"test_image_{i+1}.jpg"))
                
            print("[OK] Created test images")
        except Exception as e:
            print(f"[ERROR] Failed to create test images: {e}")
            return
            
        # Try importing required modules
        try:
            from image_to_video_creator import ImageToVideoCreator
            print("[OK] Successfully imported ImageToVideoCreator")
        except ImportError as e:
            print(f"[ERROR] Failed to import ImageToVideoCreator: {e}")
            print("Please run setup_video.bat to fix dependencies")
            return
            
        # Try creating a minimal video
        try:
            creator = ImageToVideoCreator(
                image_dir=test_dir,
                output_path="debug_output.mp4",
                transition_duration=0.5,
                slide_style="left"
            )
            
            print("Generating script...")
            script_parts = creator.generate_script()
            
            print("Converting to speech...")
            audio_files = creator.convert_to_speech(script_parts)
            
            print("Creating video...")
            creator.create_video(script_parts, audio_files)
            
            print(f"[SUCCESS] Video created at debug_output.mp4")
            
        except Exception as e:
            print(f"[ERROR] Failed during video creation: {e}")
            traceback.print_exc()
            
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        print("\nTest complete")

def main():
    print("=== VideoGenius AI Debug Tool ===")
    
    print("\n1. Checking Python version and current directory...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    check_directories()
    check_session()
    test_video_creation()
    
    print("\nDebug analysis complete. Review the output for any errors.")
    print("If you need additional help, run: python check_dependencies.py")

if __name__ == "__main__":
    main()
