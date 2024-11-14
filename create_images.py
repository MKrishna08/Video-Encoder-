"""
Create a set of images of random or chosen size. Can use as test images for playback until we find or make an optimal set of images.

Recommend choosing or creating a folder for the images to be stored in.


"""
from PIL import Image, ImageDraw
import random

def create_random_images(num_images, width, height):
    for i in range(num_images):
        # Create a blank image
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw random shapes
        for _ in range(10):
            x0, y0 = random.randint(0, width), random.randint(0, height)
            x1, y1 = random.randint(0, width), random.randint(0, height)
            
            #  x1 > x0 , y1 > y0
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            
            draw.rectangle([x0, y0, x1, y1], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        #save image
        image.save(f'./images/random_image_{i}.jpg')

create_random_images(num_images=10, width=200, height=200)
