import os
import argparse
import textwrap
import numpy as np  # Fixed import statement
import cv2
from PIL import Image

# Add better error handling for imports
try:
    from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
except ImportError:
    print("ERROR: transformers package not installed. Run: pip install transformers")
    raise

try:
    import torch
except ImportError:
    print("ERROR: torch package not installed. Run: pip install torch")
    raise

try:
    from gtts import gTTS
except ImportError:
    print("ERROR: gTTS package not installed. Run: pip install gTTS")
    raise

# Fix imports by explicitly importing needed classes with better error handling
try:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
except ImportError:
    print("\n=== MoviePy Import Error ===")
    print("Could not import moviepy.editor. This is needed for video generation.")
    print("Please run: quickfix.bat")
    print("===============================\n")
    raise

class ImageToVideoCreator:
    def __init__(self, image_dir, output_path, transition_duration=1.0, slide_style="left"):
        """
        Initialize the video creator with input directories and parameters
        
        Args:
            image_dir: Directory containing input images
            output_path: Path for the output MP4 file
            transition_duration: Duration of transitions in seconds
            slide_style: Direction of slide transition ("left", "right", "up", "down")
        """
        self.image_dir = image_dir
        self.output_path = output_path
        self.transition_duration = transition_duration
        self.slide_style = slide_style
        self.temp_dir = "temp_files"
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        # Get sorted list of image files
        self.image_files = sorted([f for f in os.listdir(image_dir) 
                                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
    def generate_script(self):
        """Generate script based on the images using pretrained model"""
        print("Generating script from images...")
        
        # Use a compatible model for image captioning
        # Using ViT-GPT2 model which is compatible with image-to-text pipeline
        try:
            caption_model = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
            print(f"Using image captioning model: nlpconnect/vit-gpt2-image-captioning")
        except Exception as e:
            print(f"Error loading primary captioning model: {e}")
            # Fallback to another model if the first one fails
            try:
                caption_model = pipeline("image-to-text", model="microsoft/git-base-coco")
                print(f"Using fallback image captioning model: microsoft/git-base-coco")
            except Exception as e2:
                print(f"Error loading fallback captioning model: {e2}")
                raise RuntimeError("Failed to load any image captioning model")
        
        # Load text generation model
        print("Loading text generation model...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        all_captions = []
        script_parts = []
        
        # First get captions for all images
        for img_file in self.image_files:
            try:
                img_path = os.path.join(self.image_dir, img_file)
                print(f"Captioning image: {img_file}")
                caption = caption_model(img_path)[0]["generated_text"]
                all_captions.append(caption)
                print(f"Caption: {caption}")
            except Exception as e:
                print(f"Error captioning image {img_file}: {e}")
                # If captioning fails for an image, use a generic caption
                all_captions.append(f"An image showing {img_file}")
        
        # Generate coherent script from captions
        context = "Create a narrative script based on these image descriptions: " + ". ".join(all_captions)
        inputs = tokenizer(context, return_tensors="pt")
        
        # Generate longer, more detailed text
        output = model.generate(
            **inputs, 
            max_length=500,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Split the generated text into parts for each image
        words = generated_text.split()
        words_per_image = max(30, len(words) // len(self.image_files))
        
        for i in range(len(self.image_files)):
            start_idx = i * words_per_image
            end_idx = min(start_idx + words_per_image, len(words))
            if start_idx >= len(words):
                script_parts.append("")
            else:
                part = " ".join(words[start_idx:end_idx])
                script_parts.append(part)
        
        return script_parts
        
    def convert_to_speech(self, script_parts):
        """Convert script parts to speech using gTTS"""
        print("Converting script to speech...")
        audio_files = []
        
        for i, text in enumerate(script_parts):
            if not text.strip():
                continue
                
            audio_file = os.path.join(self.temp_dir, f"audio_{i}.mp3")
            tts = gTTS(text=text, lang='en', tld='com', slow=False)
            tts.save(audio_file)
            audio_files.append(audio_file)
            
        return audio_files
        
    def create_video(self, script_parts, audio_files):
        """Create video with images, script and audio"""
        print("Creating video...")
        
        clips = []
        
        for i, (img_file, audio_file) in enumerate(zip(self.image_files, audio_files)):
            # Load image and audio
            img_path = os.path.join(self.image_dir, img_file)
            audio_clip = AudioFileClip(audio_file)
            
            # Create image clip with duration matching the audio
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration)
            
            # Set audio for the image clip
            img_clip = img_clip.set_audio(audio_clip)
            
            # Apply slide-in/out effect
            if i > 0:  # Apply slide-in effect for all images except the first one
                img_clip = self.apply_slide_transition(img_clip, "in")
                
            if i < len(self.image_files) - 1:  # Apply slide-out for all except the last image
                img_clip = self.apply_slide_transition(img_clip, "out")
                
            clips.append(img_clip)
            
        # Concatenate clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Write output file
        final_clip.write_videofile(self.output_path, fps=24, codec='libx264', audio_codec='aac')
        print(f"Video created successfully: {self.output_path}")
        
        # Clean up temporary files
        self.cleanup()
        
    def apply_slide_transition(self, clip, direction_type):
        """Apply slide in/out transition effect"""
        w, h = clip.size
        duration = min(self.transition_duration, clip.duration / 2)
        
        if direction_type == "in":
            def slide_in(t):
                if t < duration:
                    progress = t / duration
                    if self.slide_style == "left":
                        return {'x': (1-progress) * w, 'y': 0}
                    elif self.slide_style == "right":
                        return {'x': (progress-1) * w, 'y': 0}
                    elif self.slide_style == "up":
                        return {'x': 0, 'y': (1-progress) * h}
                    else:  # down
                        return {'x': 0, 'y': (progress-1) * h}
                else:
                    return {'x': 0, 'y': 0}
            return clip.set_position(slide_in)
            
        else:  # out
            def slide_out(t):
                if t > clip.duration - duration:
                    progress = (t - (clip.duration - duration)) / duration
                    if self.slide_style == "left":
                        return {'x': -progress * w, 'y': 0}
                    elif self.slide_style == "right":
                        return {'x': progress * w, 'y': 0}
                    elif self.slide_style == "up":
                        return {'x': 0, 'y': -progress * h}
                    else:  # down
                        return {'x': 0, 'y': progress * h}
                else:
                    return {'x': 0, 'y': 0}
            return clip.set_position(slide_out)
    
    def cleanup(self):
        """Remove temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

def main():
    parser = argparse.ArgumentParser(description='Create a video from images with AI-generated script')
    parser.add_argument('--image_dir', required=True, help='Directory containing input images')
    parser.add_argument('--output', default='output.mp4', help='Output MP4 file path')
    parser.add_argument('--transition', type=float, default=1.0, help='Transition duration in seconds')
    parser.add_argument('--slide', default='left', choices=['left', 'right', 'up', 'down'], 
                        help='Slide transition direction')
    
    args = parser.parse_args()
    
    creator = ImageToVideoCreator(
        image_dir=args.image_dir,
        output_path=args.output,
        transition_duration=args.transition,
        slide_style=args.slide
    )
    
    script_parts = creator.generate_script()
    audio_files = creator.convert_to_speech(script_parts)
    creator.create_video(script_parts, audio_files)

if __name__ == "__main__":
    main()
