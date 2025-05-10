from PIL import Image, ImageDraw
import os

def create_icon(platform = "mac"):
    icon_ = {"win": "icon.ico", "mac": "icon.icns"}
    # Create a new image with a light blue background
    size = 256
    image = Image.new('RGBA', (size, size), (173, 216, 230, 255))  # Light blue color
    
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    
    # Draw a simple "F" in the center
    text = "F"
    # Calculate text position to center it
    text_width = draw.textlength(text)
    text_height = size * 0.4
    position = ((size - text_width) / 2, (size - text_height) / 2)
    
    # Draw the text
    draw.text(position, text, fill=(0, 0, 0, 255))  # Black text
    
    # Save as icon in the assets directory
    icon_path = os.path.join(os.path.dirname(__file__), icon_[platform])
    image.save(icon_path)

if __name__ == '__main__':
    create_icon() 