import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, output_path):
    """Create a simple icon with the given size"""
    # Create a new image with blue background
    img = Image.new('RGB', (size, size), color=(67, 97, 238))
    draw = ImageDraw.Draw(img)
    
    # Draw a white circle in the center
    margin = size // 4
    draw.ellipse([(margin, margin), (size - margin, size - margin)], fill=(255, 255, 255))
    
    # Draw a video camera icon in the center
    inner_margin = size // 3
    draw.rectangle([(inner_margin, inner_margin), (size - inner_margin, size - inner_margin)], fill=(247, 37, 133))
    
    # Save the image
    img.save(output_path)
    print(f"Created icon at {output_path}")

def create_favicon(output_path):
    """Create a favicon.ico file"""
    # Create icons of different sizes
    sizes = [16, 32, 48]
    icons = []
    
    for size in sizes:
        img = Image.new('RGB', (size, size), color=(67, 97, 238))
        draw = ImageDraw.Draw(img)
        margin = size // 4
        draw.ellipse([(margin, margin), (size - margin, size - margin)], fill=(255, 255, 255))
        inner_margin = size // 3
        draw.rectangle([(inner_margin, inner_margin), (size - inner_margin, size - inner_margin)], fill=(247, 37, 133))
        icons.append(img)
    
    # Save as ICO file
    icons[0].save(output_path, format='ICO', sizes=[(size, size) for size in sizes])
    print(f"Created favicon at {output_path}")

if __name__ == "__main__":
    # Ensure the directory exists
    os.makedirs('static/images', exist_ok=True)
    
    # Create PWA icons
    create_icon(192, 'static/images/icon-192.png')
    create_icon(512, 'static/images/icon-512.png')
    
    # Create favicon
    create_favicon('static/images/favicon.ico')
    
    print("All icons created successfully!")
