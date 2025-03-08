# Image to Video Creator with AI Script Generation

This tool creates videos from a series of images by:
1. Using AI to generate a script based on the images
2. Converting the script to speech
3. Creating a video with synchronized images and narration

## Setup

1. Install Python 3.7+ if not already installed
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script with the following command:

```bash
python image_to_video_creator.py --image_dir /path/to/images --output output.mp4
```

### Arguments

- `--image_dir` (required): Directory containing the input images
- `--output`: Output MP4 file path (default: output.mp4)
- `--transition`: Transition duration in seconds (default: 1.0)
- `--slide`: Slide transition direction ('left', 'right', 'up', 'down') (default: 'left')

## Example

```bash
python image_to_video_creator.py --image_dir ./my_images --output my_video.mp4 --transition 0.8 --slide right
```

## Notes

- Images should be in JPG, JPEG, or PNG format
- Images will be processed in alphabetical order
- The script uses gpt2 for text generation and BLIP for image captioning
- Internet connection is required for downloading models on first use
