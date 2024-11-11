
import os
import cv2

class ImageProcessor:
    """
    Handles image retrieval and processing tasks.
    """
    SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')

    def __init__(self, input_folder, width, height, verbose=False):
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
        self.image_files = self._get_image_files()

    def _get_image_files(self):
        """
        Retrieves and sorts image files from the input folder.

        Returns:
            list: Sorted list of image file paths.
        """
        image_files = [
            os.path.join(self.input_folder, file)
            for file in os.listdir(self.input_folder)
            if file.lower().endswith(self.SUPPORTED_EXTENSIONS)
        ]
        image_files.sort()
        if self.verbose:
            print(f"Found {len(image_files)} image(s) to process.")
        return image_files

    def process_images(self):
        """
        Processes images by reading and resizing them.

        Yields:
            numpy.ndarray: Processed image frames.
        """
        for idx, img_path in enumerate(self.image_files):
            image = cv2.imread(img_path)
            if image is None:
                if self.verbose:
                    print(f"Warning: Unable to read image '{img_path}'. Skipping.")
                continue
            resized_image = cv2.resize(image, (self.width, self.height))
            if self.verbose:
                print(f"Processed {idx + 1}/{len(self.image_files)}: '{img_path}'")
            yield resized_image
