
import cv2
import os
import glob

class ImageProcessor:
    def __init__(self, input_folder, width = 640, height = 480, verbose = False):
        """
        Initializes the ImageProcessor.

        Args:
            input_folder (str): Path to the input images folder.
            width (int): Target width for resizing.
            height (int): Target height for resizing.
            verbose (bool): If True, enables verbose output.
        """
        self.input_folder = input_folder
        self.width = width
        self.height = height
        self.verbose = verbose

    def process_images(self):
        """
        Processes images by reading and resizing them.

        Yields:
            numpy.ndarray: Processed image frames.
        """

        #Get the image path from the folder
        print('image processing')
        images = glob.glob(os.path.join(self.input_folder, '*.jpg'))
        images.sort()

        if self.verbose:
            print(f"Found {len(images)} image(s) to process.")
        else:
            print("Images not found!")
            return

        for idx, image_path in enumerate(images):
            frame = cv2.imread(image_path)
            if image_path is None:
                if self.verbose:
                    print(f"Warning: Unable to read image '{image_path}'. Skipping.")
                continue

            resized_image = cv2.resize(frame, (self.width, self.height))
            if self.verbose and idx%10 == 0:
                print(f"Processed {idx + 1}/{len(images)}: '{image_path}'")
            
            yield resized_image
