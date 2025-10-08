"""Simple script to create a test image for ImageLoader"""

from PIL import Image, ImageDraw
import os

def create_test_image():
    # Create a simple test image
    width, height = 1280, 720
    image = Image.new('RGB', (width, height), color='red')
    
    # Draw some shapes to make it visually distinct
    draw = ImageDraw.Draw(image)
    draw.rectangle([100, 100, 300, 300], fill='blue', outline='white')
    draw.ellipse([400, 100, 700, 400], fill='green', outline='yellow')
    draw.text([300, 450], "TEST IMAGE", fill='white')
    
    # Save the test image
    test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
    image.save(test_image_path)
    print(f"Test image created: {test_image_path}")
    return test_image_path

if __name__ == "__main__":
    create_test_image()