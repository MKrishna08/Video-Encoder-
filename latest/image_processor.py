# image_processor.py

import os
import cv2

class ImageProcessor:
    def __init__(self, input_folder, verbose=False):
        self.input_folder = input_folder
        self.verbose = verbose
        self.image_files = sorted([
            os.path.join(input_folder, f) for f in os.listdir(input_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ])

    def process_images(self):
        for idx, image_path in enumerate(self.image_files, start=1):
            frame = cv2.imread(image_path)
            if frame is None:
                if self.verbose:
                    print(f"Warning: Unable to read {image_path}")
                continue
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.verbose:
                print(f"Processing frame {idx}: {image_path}")
            yield frame_rgb
