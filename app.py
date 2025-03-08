import os
import uuid
import json
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename

# Try importing ImageToVideoCreator, but provide a fallback if it fails
try:
    from image_to_video_creator import ImageToVideoCreator
    # Further validate that all needed packages work
    try:
        import torch
        import numpy as np
        from transformers import pipeline
        from gtts import gTTS
        from moviepy.editor import AudioFileClip
        video_creator_available = True
    except ImportError as e:
        print(f"Warning: Video generation dependencies incomplete: {e}")
        print("Please run setup_video.bat to install all required dependencies.")
        video_creator_available = False
except ModuleNotFoundError as e:
    print(f"Warning: ImageToVideoCreator module not available: {e}")
    print("Please run setup_video.bat to install all required dependencies.")
    video_creator_available = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], 'static/images']:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# Serve service worker from root path for PWA support
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

# Serve PWA icons and favicon
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/api/upload', methods=['POST'])
def upload_images():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    # Create session directory
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save uploaded files
    file_paths = []
    for file in files:
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(session_dir, filename)
            file.save(file_path)
            file_paths.append(file_path)
    
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'file_count': len(file_paths),
        'message': f'Successfully uploaded {len(file_paths)} images'
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    if not video_creator_available:
        return jsonify({
            'error': 'Video generation is currently disabled due to missing dependencies.',
            'solution': 'Please run the setup_video.bat file to install all required dependencies.'
        }), 503
    
    data = request.json
    session_id = data.get('session_id')
    transition_duration = float(data.get('transition', 1.0))
    slide_style = data.get('slide', 'left')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    if not os.path.exists(session_dir):
        return jsonify({'error': 'Invalid session ID'}), 400
    
    # Check if directory is empty or has no valid images
    image_files = [f for f in os.listdir(session_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        return jsonify({'error': 'No valid images found in the session directory'}), 400
    
    # Set up output file path
    output_filename = f"{session_id}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        print(f"Starting video generation for session: {session_id}")
        print(f"Found {len(image_files)} images in directory")
        print(f"Transition duration: {transition_duration}, Style: {slide_style}")
        
        # Create video from images
        creator = ImageToVideoCreator(
            image_dir=session_dir,
            output_path=output_path,
            transition_duration=transition_duration,
            slide_style=slide_style
        )
        
        # Generate script, convert to speech, and create video
        print("Generating script...")
        script_parts = creator.generate_script()
        
        print("Converting to speech...")
        audio_files = creator.convert_to_speech(script_parts)
        
        print("Creating video...")
        creator.create_video(script_parts, audio_files)
        
        video_url = f"/output/{output_filename}"
        print(f"Video created successfully at {video_url}")
        return jsonify({
            'status': 'success',
            'video_url': video_url,
            'message': 'Video created successfully'
        })
    except Exception as e:
        print(f"ERROR during video generation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Error generating video: {str(e)}',
            'details': traceback.format_exc()
        }), 500

@app.route('/output/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/api/status/<session_id>')
def check_status(session_id):
    # In a production app, this would check the actual processing status
    # For now, we'll just verify the session exists
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}.mp4")
    
    if os.path.exists(output_file):
        status = "complete"
        progress = 100
    elif os.path.exists(session_dir):
        status = "processing"
        progress = 50  # Simulate progress
    else:
        status = "not_found"
        progress = 0
        
    return jsonify({
        'status': status,
        'progress': progress,
        'session_id': session_id
    })

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'version': '1.0.0'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Check if icons exist, otherwise generate them
    icon_paths = ['static/images/icon-192.png', 'static/images/icon-512.png', 'static/images/favicon.ico']
    if not all(os.path.exists(path) for path in icon_paths):
        try:
            import create_icons
            create_icons.create_icon(192, 'static/images/icon-192.png')
            create_icons.create_icon(512, 'static/images/icon-512.png')
            create_icons.create_favicon('static/images/favicon.ico')
            print("Generated missing icon files.")
        except Exception as e:
            print(f"Could not generate icons: {e}")
            print("Please run 'python create_icons.py' manually.")
    
    # Show additional diagnostic information
    print("\n=== VideoGenius AI ===")
    print("Server starting at http://127.0.0.1:5000")
    print(f"Video generation functionality is {'ENABLED' if video_creator_available else 'DISABLED'}")
    if not video_creator_available:
        print("\nTo enable video generation, run: setup_video.bat\n")
    
    app.run(debug=True)
